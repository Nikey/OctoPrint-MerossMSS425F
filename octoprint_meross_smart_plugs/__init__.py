import asyncio
import octoprint.plugin
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager


async def shutdown(email, password, m_device_type, m_device_name, delay, plug_channel):
        http_api_client = await MerossHttpClient.async_from_user_password(email=email, password=password)
        manager = MerossManager(http_client=http_api_client)
        await manager.async_init()
        await manager.async_device_discovery()
        if device_type=="MSS210":
                plugs = manager.find_devices(device_type='mss210', device_name=m_device_name)
                if len(plugs) > 0:
                        plug = plugs[0]
                        await plug.async_update()
                        await asyncio.sleep(delay)
                        await plug.async_turn_off()
        else:
                plugs = manager.find_devices(device_type='mss425e', device_name=m_device_name, channel=plug_channel) or manager.find_devices(device_type='mss425f', device_name=m_device_name, channel=plug_channel)
                if len(plugs) > 0:
                        plug = plugs[0]
                        for id_plug in id_plugs:
                                await plug.async_update()
                                await asyncio.sleep(1)
                                await plug.async_turn_off(channel=id_plug)
                                await asyncio.sleep(1)
                manager.close()
                await http_api_client.async_logout()

class MerossSmartPlugsPlugin(octoprint.plugin.AssetPlugin,
                                                  octoprint.plugin.SettingsPlugin,
                                                  octoprint.plugin.StartupPlugin,
                                                  octoprint.plugin.TemplatePlugin):

        ##~~ SettingsPlugin mixin

        def get_settings_defaults(self):
                return dict(
                        email='',
                        password='',
                        device_type='MSS210',
                        device_name='',
                        delay=0,
                        multiplug = dict(
                                first_plug=False,
                                second_plug=False,
                                third_plug=False,
                                fourth_plug=False,
                                usb_plug=False
                        )
                )

        def get_template_configs(self):
                return [
                        dict(type='settings', custom_bindings=False)
                ]

        ##~~ AssetPlugin mixin

        def get_assets(self):
                return dict(
                        less=["less/meross-smart-plugs.less"]
                )

        ##~~ Softwareupdate hook

        def get_update_information(self):
                # Define the configuration for your plugin to use with the Software Update
                # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
                # for details.
                return dict(
                        meross_smart_plugs=dict(
                                displayName="Octoprint-Meross Smart Plugs Plugin",
                                displayVersion=self._plugin_version,

                                # version check: github repository
                                type="github_release",
                                user="Nikey",
                                repo="OctoPrint-MerossSmartPlugs",
                                current=self._plugin_version,

                                # update method: pip
                                pip="https://github.com/Nikey/OctoPrint-MerossSmartPlugs/archive/{target_version}.zip"
                        )
                )

        def hook_gcode_queuning(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
                if gcode == 'M81':
                        email = self._settings.get(['email'])
                        password = self._settings.get(['password'])
                        device_type = self._settings.get(['device_type'])
                        device_name = self._settings.get(['device_name'])
                        delay = self._settings.get(['delay'])

                        multiplug = self._settings.get(['multiplug'])
                        plug_channel = []
                        if 'first_plug' in multiplug and multiplug['first_plug'] is True:
                                plug_channel.append(1)
                        if 'second_plug' in multiplug and multiplug['second_plug'] is True:
                                plug_channel.append(2)
                        if 'third_plug' in multiplug and multiplug['third_plug'] is True:
                                plug_channel.append(3)
                        if 'fourth_plug' in multiplug and multiplug['fourth_plug'] is True:
                                plug_channel.append(4)
                        if 'usb_plug' in multiplug and multiplug['usb_plug'] is True:
                                plug_channel.append(5)

                        if email != '' and password != '':
                                asyncio.create_task(shutdown(email, password, device_type, device_name, delay, plug_channel))
                        else:
                                self._logger.info('Connection information are not been set!')


__plugin_name__ = "Meross Smart Plugs"
__plugin_pythoncompat__ = ">=2.7,<4"

def __plugin_load__():
        global __plugin_implementation__
        __plugin_implementation__ = MerossSmartPlugsPlugin()

        global __plugin_hooks__
        __plugin_hooks__ = {
                "octoprint.comm.protocol.gcode.queuing": __plugin_implementation__.hook_gcode_queuning,
                "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
        }

