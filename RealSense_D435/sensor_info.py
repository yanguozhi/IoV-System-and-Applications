import pyrealsense2 as rs

if __name__ == '__main__':
	try:
		# Create a pipeline
		pipe = rs.pipeline()
		# Create a default configuration
		cfg = rs.config()
		print("Pipeline is created")
		print("Searching Devices..")
		# Store connected device(s)
		selected_devices = []

		for d in rs.context().devices:
			selected_devices.append(d)
			print('Find Device:', d.get_info(rs.camera_info.name))
		if not selected_devices:
			print("No RealSense device is connected!")

		rgb_sensor = depth_sensor = None
		for device in selected_devices:
			print("Required sensors for device:", device.get_info(rs.camera_info.name))
			# Show available sensors in each device
			for s in device.sensors:
				if s.get_info(rs.camera_info.name) == 'RGB Camera':
					print(" - RGB sensor found")
					rgb_sensor = s  # Set RGB sensor
				if s.get_info(rs.camera_info.name) == 'Stereo Module':
					depth_sensor = s  # Set Depth sensor
					print(" - Depth sensor found")

	except Exception as e:
		print(e)
		pass
