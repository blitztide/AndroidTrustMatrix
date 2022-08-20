from configparser import ConfigParser


config = ConfigParser()
config.read('config/config.ini')

def get_db_config():
    username = config.get('db','username')
    password = config.get('db','password')
    host = config.get('db','host')
    port = config.get('db','port')
    database = config.get('db','database')
    return (username, password, host, port, database)

def get_proxy_config():
    http = config.get('proxy','http')
    https = config.get('proxy','https')
    proxy = { "http": http, "https": https}
    return proxy

def get_repo_dir():
    repodir = config.get('repo','repodir')
    return repodir

def get_clam_socket():
    socketadd = config.get('clamav','unixsock')
    return socketadd