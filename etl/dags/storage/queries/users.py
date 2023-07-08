from dags.storage import get_engine


def get_client_id_by_team_id(team_id: int) -> str:
    q = f"""SELECT "clientId" FROM app."Team" WHERE "id" = '{team_id}'"""
    client_id = get_engine().execute(q).scalar()
    return client_id
