# no standard tests in this file, ignore
__test__ = False

if __name__ == '__main__':
    import eventlet
    eventlet.monkey_patch()
    from eventlet.green import subprocess

    subprocess.Popen(['true'], stdin=subprocess.PIPE).wait()
    print("done")
