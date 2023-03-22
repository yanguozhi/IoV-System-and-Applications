# Demonstrate a way of performing background removal by
# aligning depth images to color images and performing
# simple calculation to strip the background.


import cv2
import numpy as np
import pyrealsense2 as rs
import matplotlib.pyplot as plt

if __name__ == '__main__':
	# Create a pipeline
	pipeline = rs.pipeline()

	# Create a config and configure the pipeline to
	# stream different resolutions of color and depth streams
	config = rs.config()
	config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
	config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

	# Start streaming
	profile = pipeline.start(config)

	# Getting the depth sensor's depth scale， which means the length(m) of per depth
	depth_sensor = profile.get_device().first_depth_sensor()
	depth_scale = depth_sensor.get_depth_scale()

	# We will be removing the background of objects more than
	# clipping_distance_in_meters meter away (移除超过1m远的对象的背景)
	clipping_distance_in_meters = 1  # meter
	clipping_distance = clipping_distance_in_meters / depth_scale

	# Create an align object
	# rs.align allows us to perform alignment of depth frames to others frames
	# The "align_to" is the stream type to which we plan to align depth frames.
	# Upon closer inspection you can notice that the two frames are not captured from the same physical viewport.
	align_to = rs.stream.color
	align = rs.align(align_to)

	# Streaming loop
	try:
		while True:
			# Get frameset of color and depth
			frames = pipeline.wait_for_frames()

			# Align the depth frame to color frame
			aligned_frames = align.process(frames)

			# Get aligned frames
			aligned_depth_frame = aligned_frames.get_depth_frame()
			color_frame = aligned_frames.get_color_frame()

			# Validate that both frames are valid
			if not aligned_depth_frame or not color_frame:
				continue

			# Convert images to numpy arrays
			depth_image = np.asanyarray(aligned_depth_frame.get_data())
			color_image = np.asanyarray(color_frame.get_data())

			# Remove background - Set pixels further than clipping_distance to grey
			grey_color = 153
			depth_image_3d = np.dstack((depth_image, depth_image, depth_image))  # depth image is 1 channel, color is 3 channels
			bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)

			depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
			images = np.hstack((bg_removed, depth_colormap))

			cv2.namedWindow('Align Example', cv2.WINDOW_AUTOSIZE)
			cv2.imshow('Align Example', images)
			key = cv2.waitKey(1)
			# Press esc or 'q' to close the image window
			if key & 0xFF == ord('q') or key == 27:
				cv2.destroyAllWindows()
				break

	finally:
		pipeline.stop()

