
# x = cx + r * cos(a)
# y = cy + r * sin(a)
import math
import ai
AIClass="CircleBlaster"
import random
from collections import defaultdict
from world import isValidSquare
import sys
import os
sys.path.append(os.path.dirname(__file__))
import okay

THIRTY_DEGREES=(180 / math.pi) * 30

class CircleBlaster(okay.OkayAI):
    def _init(self):
      self.cluster_destination = None
      self.explorers = []
      self.expansion_phase = 0

    def _spin(self):
      # Want functions to move the units as a whole.
      available_units = filter(lambda x: not x.is_capturing, self.my_units)


      for building in self.visible_buildings:
        self.buildings[building.position] = building

      cluster_size = 5
      rotation_offset = 0


      main_circle_size = len(available_units)


      radius_m = 1
      if self.expansion_phase:
        self.expansion_phase -= 1
        radius_m = 10
      else:
        if len(self.my_units) > 10 and random.random() > 0.95:
          self.expansion_phase = random.randint(5, 10)

      if self.explorers:
        for unit in self.explorers:
          self.searcher.assign_next_destination(unit)
          unit.move(self.searcher.destinations[unit])
          available_units.remove(unit)

      for i in xrange(len(available_units)/cluster_size+2):
        rotation_offset += THIRTY_DEGREES
        unit_cluster = available_units[:(i+1)*cluster_size]
        available_units = available_units[(i+1)*cluster_size:]

        radius = math.log(self.mapsize)*main_circle_size / 2
        if self.my_buildings:
          pos = random.choice(self.my_buildings).position
        else:
          pos = random.choice(self.buildings.keys()).position
          radius = 1

        for unit in unit_cluster:
          if unit.visible_enemies:
            vunit = random.choice(unit.visible_enemies)
            self.form_circle(unit_cluster, vunit.position, 3, rotation_offset)
            break

        # Radius = 1/2 diameter
        try:
          x_pos = random.randint(0, main_circle_size/2)*unit_cluster[0].sight
          y_pos = (main_circle_size/2) - x_pos

          x_pos *= random.choice([-1, 1, 0.5, -0.5])
          y_pos *= random.choice([-1, 1, 0.5, -0.5])
          pos  = (x_pos+pos[0],y_pos+pos[1])
        except:
          pass

        self.form_circle(unit_cluster, pos, radius*radius_m, rotation_offset)

      for unit in self.my_units:
        ire = unit.in_range_enemies
        hit = False
        for vunit in ire:
          ff = False
          hits = unit.calcVictims(vunit.position)
          for hit in hits:
            if hit.team == self.team:
              ff = True
              break

          if not ff:
            hit = True
            unit.shoot(vunit.position)
            break

        if not hit and ire:
          unit.shoot(ire[0].position)

        vb = unit.visible_buildings
        if vb:
          b = vb[0]
          if unit.team != b.team:
            if b.position == unit.position:
              unit.capture(b)
            else:
              unit.move(b.position)




    def form_circle(self, units, (x,y), radius, ro=0):
      if not units:
        return

      # So, use radians (2pi form a circle)
      radian_delta = (2*math.pi) / len(units)
      radian_offset = ro
      for unit in units:
        attempts = 0
        while True:
          radian_offset += radian_delta
          pos_x = x+(radius*math.cos(radian_offset))
          pos_y = y+(radius*math.sin(radian_offset))
          pos_x = max(min(self.mapsize, pos_x), 0)
          pos_y = max(min(self.mapsize, pos_y), 0)
          attempts += 1
          if isValidSquare((pos_x, pos_y), self.mapsize):
            break

          if attempts >= 3:
            return

        unit.move((pos_x, pos_y))

    def collapse_circle(self, units, (x,y)):
      # So, use radians (2pi form a circle)
      for unit in units:
        unit.move((x, y))

    def _unit_died(self, unit):
      if unit in self.explorers:
        self.explorers.remove(unit)

    def _unit_spawned(self, unit):
      if not self.explorers or len(self.my_units) / len(self.explorers) >= 4:
        self.explorers.append(unit)
