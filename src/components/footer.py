import streamlit as st
from pathlib import Path

def render_footer():
     st.markdown(
                """
                <div style='text-align: center; margin-top: 50px;'>
                <a href="https://www.nestle.com/" target="_blank">
                    <img src="https://1000logos.net/wp-content/uploads/2017/03/Nestle-Logo.png" alt="Nestlé Logo" width="120" style="margin-bottom: 10px;" />
                </a>    
                    <h4 style='font-size: 22px;'>🚀 Made with ❤️ by the <b>Web & Search Team</b> – NBS Cairo </h4>
                    <h4 style='font-size: 16px;'>📌 Author : <a href="mailto:omar.shaarawy@eg.nestle.com"><b>Omar Shaarawy</b></a> | Version 2.0.0</h4>
                </div>
                """,
                unsafe_allow_html=True
                ) 