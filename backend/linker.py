import abc
import os
import shutil
from typing import Callable, Dict, NamedTuple, Set


class Reference(NamedTuple):
  src_url: str


class Resource(abc.ABC):

  @abc.abstractmethod
  def get_references(self) -> Set[Reference]:
    pass

  @abc.abstractmethod
  def populate_fs(self, path: str, linker: 'Linker'):
    pass


class StaticResource(Resource):

  def __init__(self, path: str):
    super().__init__()
    self.path = path

  def get_references(self) -> Set[Reference]:
    return set()

  def populate_fs(self, path: str, _: 'Linker'):
    shutil.copyfile(self.path, path)


class LinkResource(Resource):

  def __init__(self, ref: Reference):
    super().__init__()
    self.ref = ref

  def get_references(self) -> Set[Reference]:
    return {self.ref}

  def populate_fs(self, path: str, linker: 'Linker'):
    real = linker.resolve(self.ref)
    os.symlink(real, path)


class Linker(object):

  def __init__(self):
    super().__init__()
    self._resources: Dict[Reference, Resource] = dict()
    self._link_map: Dict[Reference, str] = dict()
    self._reverse_link_map: Dict[str, Reference] = dict()

  def add_resource(self, ref: Reference, out: str, resource: Resource):
    assert ref not in self._resources
    assert ref not in self._link_map
    assert out not in self._reverse_link_map
    self._resources[ref] = resource
    self._link_map[ref] = out
    self._reverse_link_map[out] = ref

  def resolve(self, ref: Reference) -> str:
    return self._link_map[ref]

  def link(self, fs_root: str, entries: Set[Reference]):
    frontier: Set[Reference] = set(entries)
    while frontier:
      new_frontier: Set[Reference] = set()
      for ref in frontier:
        res = self._resources[ref]
        new_frontier |= set(res.get_references())
      frontier = new_frontier - set(self._link_map.keys())
    for ref, relpath in self._link_map.items():
      abspath = os.path.join(fs_root, relpath)
      os.makedirs(os.path.dirname(abspath), exist_ok=True)
      res.populate_fs(abspath, self)
