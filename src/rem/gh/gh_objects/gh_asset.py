# coding=utf-8

from src.rem.gh.gh_objects.base_gh_object import BaseGHObject, json_property
from src.rem.gh.gh_objects.gh_user import GHUser


class GHReleaseAsset(BaseGHObject):
    @json_property
    def url(self):
        """"""

    @json_property
    def id(self):
        """"""

    @json_property
    def name(self):
        """"""

    @json_property
    def label(self):
        """"""

    def uploader(self) -> GHUser:
        return GHUser(self.json['uploader'])

    @json_property
    def content_type(self):
        """"""

    @json_property
    def state(self):
        """"""

    @json_property
    def size(self):
        """"""

    @json_property
    def download_count(self):
        """"""

    @json_property
    def created_at(self):
        """"""

    @json_property
    def updated_at(self):
        """"""

    @json_property
    def browser_download_url(self):
        """"""


class GHAllReleaseAssets(BaseGHObject):
    def __iter__(self):
        for x in self.json:
            yield GHReleaseAsset(x)

    def __len__(self) -> int:
        return len(self.json)

    def __getitem__(self, item) -> GHReleaseAsset:
        for asset in self:
            if asset.name == item:
                return asset
        raise AttributeError('asset not found: {}'.format(item))

    def __contains__(self, item) -> bool:
        try:
            self.__getitem__(item)
            return True
        except AttributeError:
            return False
