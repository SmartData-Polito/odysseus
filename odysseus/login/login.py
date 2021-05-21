import streamlit as st


def is_authenticated(username, password):
    return username == 'user' and password == 'pass'


def generate_login_block():
    block1 = st.empty()
    block2 = st.empty()
    return block1, block2


def clean_blocks(blocks):
    for block in blocks:
        block.empty()


def login(blocks):
    username = blocks[0].text_input('Username')
    password = blocks[1].text_input('Password', type="password")
    return username, password
