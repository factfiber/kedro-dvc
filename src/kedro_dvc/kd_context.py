"""
Defines kedro-dvc context object, which wraps both kedro context and dvc repo.
"""
import os
from pathlib import Path
from typing import Optional

from dvc.exceptions import NotDvcRepoError
from dvc.repo import Repo as DvcRepo
from kedro.framework.project import configure_project, settings
from kedro.framework.session import KedroSession
from kedro.framework.startup import ProjectMetadata, _get_project_metadata

from . import exceptions


class KDContext:
    """
    Wrapper for kedro context, dvc repo.
    """

    def __init__(
        self,
        project_dir: Optional[os.PathLike[str]] = None,
        metadata: Optional[ProjectMetadata] = None,
        install_dvc: bool = False,
    ):
        """
        Args:
            project_dir: Path to the root of the kedro project.
                Default is metadata.project_path if provided, otherwise current
                working directory.
            metadata: Optional metadata object (initialized if not present).
        """
        if project_dir is None and metadata is not None:
            project_dir = Path(metadata.project_path)
        elif project_dir is None:
            project_dir = Path.cwd()
        self.project_path = Path(project_dir)
        self.metadata = self._ensure_metadata(metadata)
        configure_project(self.metadata.package_name)
        self.settings = settings
        self.dvc_repo = self._setup_dvc(install_dvc=install_dvc)
        self.conf_path = self.project_path / settings.CONF_SOURCE
        if not self.conf_path.exists():
            raise RuntimeError(
                f"Kedro config dir does not exist: {str(self.conf_path)}"
            )

        self.session = KedroSession.create(
            self.metadata.package_name, self.project_path
        )
        self.context = self.session.load_context()

    @property
    def project_name(self) -> str:
        return self.metadata.project_name

    def _ensure_metadata(
        self,
        metadata: Optional[ProjectMetadata] = None,
    ) -> ProjectMetadata:
        """
        Ensure metadata is available.
        """
        if metadata is None:
            metadata = _get_project_metadata(self.project_path)
        return metadata

    def _setup_dvc(self, install_dvc: bool = False) -> DvcRepo:
        """
        Return DVC Repo object.

        Ensures DVC installed in project root.
        """
        try:
            # throws NotDvcRepoError if not a dvc repo
            dvc_repo = DvcRepo(str(self.project_path))
        except NotDvcRepoError:
            if not install_dvc:
                raise
            # NB: requires .git to be present in project_dir
            dvc_repo = DvcRepo.init(str(self.project_path))
        else:
            if install_dvc:
                raise exceptions.AlreadyInstalled(
                    "DVC already installed. (Run update to update config.)"
                )
        return dvc_repo
