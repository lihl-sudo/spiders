from rediscluster import RedisCluster
# import redis

startup_nodes = [
          {'host': 'localhost', 'port': '7001'},
          {'host': 'localhost', 'port': '7002'},
          {'host': 'localhost', 'port': '7003'},
      ]
# sr = redis.StrictRedis(host=127.0.0.1, port=6379, data=0)
rc = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)
result = rc.set("name", "lihl")
print(result)
name = rc.get("name")
print(name)
rc.delete("name")