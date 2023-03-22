import cv2
import time
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

	align_to = rs.stream.color
	align = rs.align(align_to)

	# Getting the depth sensor's depth scale， which means the length(m) of per depth
	depth_sensor = profile.get_device().first_depth_sensor()
	depth_scale = depth_sensor.get_depth_scale()
	print('Depth scale:', depth_scale)

	# capture a frame(color_frame, depth frame)
	for i in range(10):
		time.sleep(0.1)
		frames = pipeline.wait_for_frames()

	aligned_frames = align.process(frames)
	depth_frame = aligned_frames.get_depth_frame()
	color_frame = aligned_frames.get_color_frame()
	# color_frame = frames.get_color_frame()
	# depth_frame = frames.get_depth_frame()

	# Convert images to numpy arrays
	# color_image = np.asanyarray(color_frame.get_data())
	color_image = (np.asanyarray(color_frame.get_data()))[..., ::-1]
	depth_image = np.asanyarray(depth_frame.get_data())
	depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=255 / 3000), cv2.COLORMAP_JET)

	print('Color image shape:', color_image.shape)
	print('Depth image shape:', depth_image.shape)
	print('Depth Color Map shape:', depth_colormap.shape)
	print('Depth range:', [np.min(depth_image), np.max(depth_image)])

	# Get the distance: two methods
	# Calculate the distance directly
	distance_1 = depth_frame.get_distance(400, 300)  # Provide the depth in meters at the given pixel() (w, h)
	print('Distance_1 (m) of  Pixel (400, 300):', distance_1)

	# Calculate the distance by depth
	point_depth = depth_image[300, 400].astype(float)  # (h, w) (左上为0, 0)
	distance_2 = point_depth * depth_scale
	print('Point depth of Pixel (500, 300):', point_depth)
	print('Distance_2 (m) of Pixel (500, 300):', distance_2)

	# Stack both images horizontally and display
	# images = np.hstack((color_image, depth_colormap))
	plt.subplot(1, 2, 1)
	plt.imshow(color_image)
	plt.scatter(400, 300, c='r')
	plt.subplot(1, 2, 2)
	plt.imshow(depth_colormap)
	plt.scatter(400, 300, c='r')
	plt.show()
















