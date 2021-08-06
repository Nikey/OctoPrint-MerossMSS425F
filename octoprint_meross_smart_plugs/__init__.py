import asyncio
import octoprint.plugin
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager


async def shutdown(email, password):
	http_api_client = await MerossHttpClient.async_from_user_password(email=email,
																	  password=password)

	manager = MerossManager(http_client=http_api_client)
	await manager.async_init()

	await manager.async_device_discovery()
	plugs = manager.find_devices(device_type='mss210')

	if len(plugs) > 0:
		plug = plugs[0]
		await plug.async_update()
		await asyncio.sleep(1)
		await plug.async_turn_off()
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
			password=''
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

			if email != '' and password != '':
				asyncio.create_task(shutdown(email, password))
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

