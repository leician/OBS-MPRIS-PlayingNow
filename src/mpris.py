import asyncio
from threading import Lock

from jeepney import DBus, DBusAddress, MatchRule, new_method_call
from jeepney.io.asyncio import open_dbus_router


class MPRIS:
    def __init__(self, player):
        self.player = player
        self.address = DBusAddress("/org/mpris/MediaPlayer2",
                            bus_name=self.player,
                            interface="org.mpris.MediaPlayer2.Player")

        self.STOPPED_STATUS_GRACE_PERIOD = 0.5
        self.latest_metadata = {}
        self.metadata_lock = Lock()

    @staticmethod
    async def get_players():
        address = DBusAddress("/org/freedesktop/DBus",
                              bus_name="org.freedesktop.DBus",
                              interface="org.freedesktop.DBus")
        players = []

        msg = new_method_call(address, "ListNames")
        async with open_dbus_router() as router:
            reply = await router.send_and_get_reply(msg)
            for iface in reply.body[0][1]:
                if iface.startswith("org.mpris.MediaPlayer2"):
                    players.append(iface)

        return players

    async def consume_metadata(self):
        async for metadata in self.metadata_listener():
            with self.metadata_lock:
                self.latest_metadata.update(metadata)

    async def metadata_listener(self):
        rule = MatchRule(
            type = "signal",
            interface = "org.freedesktop.DBus.Properties",
            member = "PropertiesChanged",
            path = "/org/mpris/MediaPlayer2",
        )
        rule.add_arg_condition(0, self.address.interface)

        bus_rule = MatchRule(
            type = "signal",
            sender = self.address.bus_name,
            interface = "org.freedesktop.DBus.Properties",
            member = "PropertiesChanged",
            path = "/org/mpris/MediaPlayer2",
        )
        bus_rule.add_arg_condition(0, self.address.interface)

        dbus = DBus()
        async with open_dbus_router() as router:
            with router.filter(rule) as messages:
                await router.send_and_get_reply(dbus.AddMatch(bus_rule))
                try:
                    try:
                        meta = await self.mpris_metadata()
                        status = await self.mpris_playbackstatus()

                        data = {
                            "title": meta.get("xesam:title", ("s", "N/A"))[1],
                            "artists": meta.get("xesam:artist", ("as", []))[1],
                            "cover": meta.get("mpris:artUrl", ("s", ""))[1],
                            "status": status
                        }
                        yield data

                    except Exception:
                        print("Could not read initial MPRIS metadata")

                    while True:
                        signal = await messages.get()
                        changed_properties = signal.body[1]
                        updates = {}
                        metadata_variant = changed_properties.get("Metadata")
                        if metadata_variant is not None:
                            metadata = metadata_variant[1]
                            updates.update({
                                "title": metadata.get("xesam:title", ("s", "N/A"))[1],
                                "artists": metadata.get("xesam:artist", ("as", []))[1],
                                "cover": metadata.get("mpris:artUrl", ("s", ""))[1],
                            })

                        status_variant = changed_properties.get("PlaybackStatus")
                        if status_variant is not None:
                            status = status_variant[1]
                            if status == "Stopped":
                                await asyncio.sleep(self.STOPPED_STATUS_GRACE_PERIOD)
                                try:
                                    status = await self.mpris_playbackstatus()
                                except Exception:
                                    print(
                                        "Could not confirm stopped MPRIS playback status"
                                    )
                            updates["status"] = status

                        if updates:
                            yield updates

                finally:
                    await router.send_and_get_reply(dbus.RemoveMatch(bus_rule))

    async def mpris_playbackstatus(self):
        props_if = DBusAddress("/org/mpris/MediaPlayer2",
                            bus_name=self.player,
                            interface="org.freedesktop.DBus.Properties")
        msg = new_method_call(props_if,
                            "Get",
                            "ss",
                            (self.address.interface, "PlaybackStatus"))
        async with open_dbus_router() as router:
            reply = await router.send_and_get_reply(msg)
            return reply.body[0][1]

    async def mpris_metadata(self):
        props_if = DBusAddress("/org/mpris/MediaPlayer2",
                            bus_name=self.player,
                            interface="org.freedesktop.DBus.Properties")
        msg = new_method_call(props_if,
                            "Get",
                            "ss",
                            (self.address.interface, "Metadata"))
        async with open_dbus_router() as router:
            reply = await router.send_and_get_reply(msg)
            return reply.body[0][1]