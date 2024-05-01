#!/usr/bin/env python3

from os import environ, name
from pathlib import Path
from subprocess import Popen, PIPE
from contextlib import contextmanager

from typer import Exit, Typer

app = Typer()

state = {
    "jdk_path": None
}

@contextmanager
def Gradle(*tasks, env={}):
    """
    Exécute des tâches Gradle avec des options spécifiées.

    Args:
        *tasks: Liste des tâches Gradle à exécuter.
        env: Dictionnaire d'environnement personnalisé (facultatif).

    Yields:
        process: Objet Popen pour la gestion des processus.

    Example:
        with Gradle('clean', 'compileJava') as process:
            finish(process)
    """
    env = env
    tasks = tasks
    wrapper = 'gradlew.bat' if name == 'nt' else 'gradlew'
    wrapper_file = Path().resolve().joinpath(wrapper).as_posix()
    jdk_path = state['jdk_path']
    
    command = [wrapper_file,
               *tasks]
    
    if jdk_path:
        command.append(f'-Dorg.gradle.java.home={jdk_path}')


    with Popen(command, stdout=PIPE, stderr=PIPE, env=dict(environ, **env), universal_newlines=True) as process:
        yield process

def finish(process):
    """
    Gère la sortie du processus Gradle.

    Args:
        process: Objet Popen du processus Gradle.

    Raises:
        Exit: En cas d'erreur de retour du processus.

    Example:
        finish(process)
    """
    out, err = process.communicate()

    if process.returncode != 0:
        print(err)
        raise Exit(code=1)
    else:
        print(out)
        raise Exit(code=0)


@app.callback()
def main(jdk_path: str = None):
    """
    Point d'entrée du script.

    Args:
        jdk_path: Chemin personnalisé vers la JDK (facultatif).
    """
    state['jdk_path'] = jdk_path


@app.command()
def build():
    """
    Exécute les tâches Gradle pour nettoyer et compiler le code Java.
    """
    with Gradle('clean', 'compileJava') as process:
        finish(process)


@app.command()
def test():
    """
    Exécute les tâches Gradle pour nettoyer et exécuter les tests.
    """
    with Gradle('clean', 'test') as process:
        finish(process)


@app.command()
def pack():
    """
    Exécute les tâches Gradle pour nettoyer et créer un fichier WAR.
    """
    with Gradle('clean', 'bootWar') as process:
        finish(process)


@app.command()
def publish(project_id=None, token=None, token_name=None):
    """
    Publishes the project using specified GitLab credentials.

    Args:
        project_id (str): The GitLab project ID.
        token (str): The GitLab access token.
        token_name (str): The name of the GitLab token.

    Example:
        To publish the project:
        ```
        python my_script.py publish --project-id 12345 --token my_token --token-name Deploy-Token
        ```
    """
    token_name_key = 'GITLAB_TOKEN_NAME'
    token_key = 'GITLAB_TOKEN'
    project_id_key = 'GITLAB_PROJECT_ID'

    vars = {
        token_name_key: token_name or environ.get(token_name_key),
        token_key: token or environ.get(token_key),
        project_id_key: project_id or environ.get(project_id_key)
    }

    with Gradle('publish', env=vars) as process:
        finish(process)

if __name__ == '__main__':
    app()
