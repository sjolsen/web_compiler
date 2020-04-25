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
    real = linker.resolve(self.ref, absolute=True)
    real_rel = os.path.relpath(real, os.path.dirname(path))
    os.symlink(real_rel, path)


class Linker(object):

  def __init__(self, fs_root: str):
    super().__init__()
    self._fs_root = fs_root
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

  def resolve(self, ref: Reference, *, absolute: bool = False) -> str:
    if absolute:
      return os.path.join(self._fs_root, self._link_map[ref])
    else:
      return self._link_map[ref]

  def link(self, entries: Set[Reference]):
    frontier: Set[Reference] = set(entries)
    closure: Set[Reference] = set()
    while frontier:
      new_frontier: Set[Reference] = set()
      for ref in frontier:
        res = self._resources[ref]
        new_frontier |= set(res.get_references())
      closure |= frontier
      frontier = new_frontier - closure
    for ref in closure:
      abspath = self.resolve(ref, absolute=True)
      os.makedirs(os.path.dirname(abspath), exist_ok=True)
      res = self._resources[ref]
      res.populate_fs(abspath, self)
