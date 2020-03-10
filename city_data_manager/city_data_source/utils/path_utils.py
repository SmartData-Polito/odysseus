import os


def check_create_path (path):
	os.makedirs(path, exist_ok=True)
