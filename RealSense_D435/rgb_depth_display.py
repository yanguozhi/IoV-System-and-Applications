# This example demonstrates how to render depth and color images using the help of opencv and numpy

import cv2
import numpy as np
import sys
# sys.path.append('/usr/local/lib')
import pyrealsense2 as rs


if __name__ == "__main__":
	# Create a pipeline
	pipeline = rs.pipeline()

	# Create a config and configure the pipeline to
	# stream different resolutions of color and depth streams
	config = rs.config()

	config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
	config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

	# Start streaming
	pipeline.start(config)

	# align_to = rs.stream.color
	# align = rs.align(align_to)

	while True:
		# wait for a coherent pair of frames: depth and color
		frames = pipeline.wait_for_frames()
		# with align frames (depth to color)
		# aligned_frames = align.process(frames)
		# depth_frame = aligned_frames.get_depth_frame()
		# color_frame = frames.get_color_frame()

		# without_align
		depth_frame = frames.get_depth_frame()
		color_frame = frames.get_color_frame()
		if not depth_frame or not color_frame:
			continue

		# Convert images to numpy arrays
		depth_image = np.asanyarray(depth_frame.get_data())
		color_image = np.asanyarray(color_frame.get_data())

		# Apply colormap on depth image (image must be converted to 8-bit per pixel first)
		depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=255/8000), cv2.COLORMAP_JET)

		# Stack both images horizontally
		images = np.hstack((color_image, depth_colormap))

		# Show  images
		cv2.namedWindow('Realsense:', cv2.WINDOW_AUTOSIZE)
		cv2.imshow('Realsense:', images)
		key = cv2.waitKey(1)
		# Press esc or 'q' to close the image window
		if key & 0xFF == ord('q') or key == 27:
			cv2.destroyAllWindows()
			break

	# Stop streaming
	pipeline.stop()
