import pyopencl as cl

platforms = cl.get_platforms()
print("Platforms available: ", len(platforms))
for platform in platforms:
    for dev in platform.get_devices():
        print (dev.name)
