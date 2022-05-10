import contextlib
import os
import pathlib
import shutil
import sys
import tempfile
from typing import Callable, Iterator, Optional, Sequence, Tuple, cast

root = os.getcwd()

AddToEnvironContext = Iterator[Callable[[str, str], None]]


@contextlib.contextmanager
def changed_environ() -> AddToEnvironContext:
    """
    Modify environment in context, and restore it on close.
    """

    added_to_environ = {}

    def add(key: str, value: str) -> None:
        added_to_environ[key] = os.environ.get(key)
        os.environ[key] = value

    try:
        yield add
    finally:
        for key, old in added_to_environ.items():
            if old is not None:
                os.environ[key] = old
            else:
                del os.environ[key]


@contextlib.contextmanager
def add_python_path(path: os.PathLike[str]) -> Iterator[None]:
    """
    Add a path to the PYTHONPATH in the context, and restore it on close.
    """
    try:
        sys.path.insert(0, str(path))
        yield
    finally:
        sys.path.remove(str(path))


@contextlib.contextmanager
def to_tmp_dir() -> Iterator[pathlib.Path]:
    """
    Create temp directory, yield context within it.
    """
    with tempfile.TemporaryDirectory() as dir:
        prev_dir = os.getcwd()
        os.chdir(dir)
        try:
            yield pathlib.Path(dir)
        finally:
            try:
                os.chdir(prev_dir)
            except Exception:  # pragma: no cover
                print(
                    "WARNING: Couldn't change back to previous"
                    + f" directory after test: {str(prev_dir)}"
                )
                os.chdir(root)


@contextlib.contextmanager
def to_memoized_dir(
    cache_dir: pathlib.Path,
    ignore_cache: bool = False,
    link: Sequence[str] = (),
) -> Iterator[Tuple[pathlib.Path, Optional[Callable[[], None]]]]:
    """
    Create temp dir; fill from cache if exists; yield context within it.

    If the cache dir is empty, `save_cache` will be a function that
    will save the cache. Otherwise, it will be None.

    Returns: tuple of (`dir`, `save_cache`):
        dir: pathlib.Path to the created directory
        save_cache: optional callable to save the cache to the `cache_dir`
    """
    with to_tmp_dir() as tmp_dir:
        save_cache: Optional[Callable[[], None]] = None
        if (
            cache_dir.exists()
            and len(os.listdir(cache_dir)) != 0
            and not ignore_cache
        ):
            if len(link) == 0:
                shutil.copytree(
                    str(cache_dir), str(tmp_dir), dirs_exist_ok=True
                )
            else:
                copy_link_tree(cache_dir, tmp_dir, link)

        else:
            if cache_dir.exists() and len(os.listdir(cache_dir)) != 0:
                shutil.rmtree(cache_dir)
                # for f in cache_dir.iterdir():
                #     if f.is_file():
                #         f.unlink()
                #     else:
                #         shutil.rmtree(f)
            save_cache = cast(
                Callable[[], None],
                lambda: shutil.copytree(
                    str(tmp_dir), str(cache_dir), dirs_exist_ok=True
                ),
            )
        yield tmp_dir, save_cache


def copy_link_tree(
    src: os.PathLike[str], dest: os.PathLike[str], link: Sequence[str]
) -> None:
    """
    Copy a directory tree, but omit the files in the link list, linking them instead.
    """
    src = pathlib.Path(src)
    dest = pathlib.Path(dest)
    for f in src.iterdir():
        if f.name in link:
            os.symlink(str(f), str(dest / f.name))
        elif f.is_dir():
            shutil.copytree(str(f), str(dest / f.name))
        else:
            shutil.copy2(str(f), str(dest / f.name))
