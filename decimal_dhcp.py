#!/usr/bin/env python
import random

import json
import argparse

import tornado.ioloop
import tornado.web


def get_options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--slots-number", dest="slots_number", type=int, help="Slots number. Ex: XXXX", required=True)
    parser.add_argument("-m", "--masked-slots", dest="masked_slots", type=int, help="Masked slots. Ex XXXYY", required=True)
    parser.add_argument("-p", "--prefixed-slots", dest="prefixed_slots", help="Prefixed slots. Ex: 102YY", required=True)
    parser.add_argument("-u", "--users-number", dest="users_number", type=int, help="Users number.", required=True)
    parser.add_argument("port", metavar="port", type=int, help="Listening port")
    options = parser.parse_args()
    assert options.slots_number == options.masked_slots + len(str(options.users_number)), "slots number can not be bigger than masked + len(users)"
    assert options.masked_slots == len(options.prefixed_slots), "slots masked must be equal to len(prefixed_slots)"
    return options


class MainHandler(tornado.web.RequestHandler):

    def __init__(self, *args, **kwargs):
        self.clients = kwargs.pop("clients")
        self.options = kwargs.pop("options")
        self.random_students = kwargs.pop("random_students")
        super(MainHandler, self).__init__(*args, **kwargs)

    def get(self):
        host = self.request.remote_ip
        if host not in self.clients:
            self.clients[host] = self.options.prefixed_slots + str(next(self.random_students)).zfill(self.options.slots_number - len(self.options.prefixed_slots))
        self.write(str(self.clients[host]) + "\n")
        print("########## {} ##########\n{}".format(len(self.clients), json.dumps(self.clients, indent=4)))


def make_app(clients, options, random_students):
    return tornado.web.Application([
        (r"/", MainHandler, dict(clients=clients, options=options, random_students=random_students))
    ])

if __name__ == "__main__":
    clients = {}
    options = get_options()
    port = options.port
    random_students = iter(random.sample(range(1, options.users_number + 1), options.users_number))

    app = make_app(clients, options, random_students)
    app.listen(port)
    print("Listening on {} with: {}".format(port, options))
    tornado.ioloop.IOLoop.current().start()
