#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import codecs
import telnetlib
import sys
import datetime
import json

with open("config_path.txt") as file:
  addpac_cfg_path = data = file.read().replace("\n", "")

with open(addpac_cfg_path) as json_data_file:
  addpac_cfg = json.load(json_data_file)['addpac']
print(addpac_cfg)

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

print('Content-Type: text/html; charset=utf-8' + "\n")
HOST = addpac_cfg['host']
PORT = addpac_cfg['port']
password = bytes(addpac_cfg['password'], 'utf-8')
user = bytes(addpac_cfg['login'], 'utf-8')

tn = telnetlib.Telnet(HOST, PORT, 5)
tn.read_until(b"Login: ", 5)
tn.write(user + b"\n")
tn.read_until(b"Password: ", 5)
tn.write(password + b"\n")
tn.read_until(b"GS1002> ", 5)
tn.write(b"en" + b"\n")
tn.read_until(b"GS1002#", 5)
tn.write(b"mobile 0 0 sms message list all" + b"\n")
tn.read_until(
    b'Index SimIndex     PhoneNumber                      Date  Message ', 5)
tn.read_until(
    b'----------------------------------------------------------------------------------',
    5)
lines = tn.read_until(
    b"----------------------------------------------------------------------------------",
    5) \
  .decode("utf-8") \
  .replace(
    "----------------------------------------------------------------------------------",
    "") \
  .split("\n")


def string_to_record(line):
  field_name_offsets_map = {0: "Index",
                            5: "SimIndex",
                            14: "PhoneNumber",
                            30: "Date",
                            56: "Message"}
  field_off_sets = list(field_name_offsets_map.keys())
  if len(line) > field_off_sets[len(field_off_sets) - 1]:
    line = line.replace("\r", "")
    result_list = {}
    old = 0
    for i in field_off_sets:
      if i != field_off_sets[0] & i != field_off_sets[len(field_off_sets) - 1]:
        result_list[field_name_offsets_map[old]] = (line[old:i].strip())
        old = i
      if i == field_off_sets[len(field_off_sets) - 1]:
        result_list[field_name_offsets_map[i]] = (line[i:].strip())
  else:
    result_list = []
  return result_list


def set_date(rec):
  # Sat Feb 27 22:17:10 2021
  rec["Date"] = datetime.datetime.strptime(rec["Date"], '%a %b %d %H:%M:%S %Y')
  return rec;


recs = filter(lambda rec: len(rec) != 0, map(string_to_record, lines))
recs = map(set_date, recs)

for o in recs:
  print(o)
