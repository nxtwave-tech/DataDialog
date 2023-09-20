import os

import streamlit as st

from sql_agent import get_sql_query_from_user_query, get_db_data_with_sql_query
from visualization import get_suggested_visualization_response_from_ai, \
    plot_visualization_for_user_query


# Streamlit page config
st.set_page_config(
    page_title="Chat with SQL Data",
    page_icon="🦜",
    layout="wide"
)
st.title("🦜 Chat with SQL Data")

# Taking open api key as user input
user_input_placeholder = st.empty()
if 'openai_api_key_input' not in st.session_state:
    openai_api_key_input = user_input_placeholder.text_input(
        "OpenAI API Key", type="password")
    if openai_api_key_input:
        # Save the input into session state
        st.session_state.openai_api_key_input = True
        os.environ['OPENAI_API_KEY'] = openai_api_key_input
        user_input_placeholder.empty()
    else:
        st.stop()


# Appending Initial message
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "How can I help you?"
         }
    ]

# Rendering existing messages
for message in st.session_state.messages:
    if 'df_content' in message:
        st.chat_message(message["role"]).dataframe(
            message["df_content"], hide_index=True)
    else:
        st.chat_message(message["role"]).write(message["content"])


# user input query placeholder
user_query = st.chat_input(placeholder="Ask me about your data!")


if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        sql_query = get_sql_query_from_user_query(user_query)
        if sql_query:
            query_op_df = get_db_data_with_sql_query(sql_query)

            # save the query result in session state
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "df_content": query_op_df
                }
            )

            # display the query result
            st.dataframe(query_op_df, hide_index=True)

            with st.spinner("Looking for a visualization to display the data..."):

            # Asking the LLM to suggest an appropriate visualization for chat input & the SQL returned from the SQL Agent
                visualization_response = get_suggested_visualization_response_from_ai(
                    sql_query, user_query)

                plot_visualization_for_user_query(
                    visualization_response, query_op_df)
        else:
            print("Cannot Find SQL Query for user query :", user_query)
