# no standard tests in this file, ignore
__test__ = False

if __name__ == '__main__':
    import subprocess
    import eventlet
    eventlet.monkey_patch(all=False, os=True)
    process = subprocess.Popen("sleep 0.1 && false", shell=True)
    print(process.wait())
