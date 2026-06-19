import asyncio
import time

def sync_task(name, seconds):
    print(f"{name} Starting....")
    time.sleep(seconds)
    print(f"{name} done!")

start= time.time()
sync_task("Task A", 2)
sync_task("Task B", 2)
end = time.time()

print(f"\nTotal Time (sync):{end- start:.2f} seconds")

async def asyn_task(name, seconds):
    print(f"{name} Starting....")
    await asyncio.sleep(seconds)
    print(f"{name} Done...")

async def main():
    start = time.time()
    await asyncio.gather(
        asyn_task("Task C", 2),
        asyn_task("Task D", 2)
    )
    end = time.time()
    print(f"\nTotal Time (async):{end - start:.2f} seconds")
asyncio.run(main())