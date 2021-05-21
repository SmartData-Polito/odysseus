from streamlit.report_thread import get_report_ctx
import streamlit as st


class SessionState(object):
    def __init__(self, **kwargs):
        """A new SessionState object.

        Parameters
        ----------
        **kwargs : any
            Default values for the session state.
        """
        for key, val in kwargs.items():
            setattr(self, key, val)


@st.cache(allow_output_mutation=True)
def get_session(id, **kwargs):
    return SessionState(**kwargs)


def get(**kwargs):
    """Gets a SessionState object for the current session.

    Creates a new object if necessary.

    Parameters
    ----------
    **kwargs : any
        Default values you want to add to the session state, if we're creating a
        new one.
    """
    ctx = get_report_ctx()
    id = ctx.session_id
    return get_session(id, **kwargs)
