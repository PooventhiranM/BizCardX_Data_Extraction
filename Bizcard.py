import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
import mysql.connector as mysql
from PIL import Image
import cv2
import os
import matplotlib.pyplot as plt
import re

# SETTING PAGE CONFIGURATIONS
icon = Image.open("C:/Users/poove/Downloads/icon.png")
st.set_page_config(page_title= "BizCardX: Extracting Business Card Data with OCR | By Pooventhiran",
                   page_icon= icon,
                   layout= "wide",
                   initial_sidebar_state= "expanded",
                   menu_items={'About': """# This OCR app is created by *Pooventhiran*!"""})
st.markdown("<h1 style='text-align: center; color: white;'>BizCardX: Extracting Business Card Data with OCR</h1>", unsafe_allow_html=True)

# # SETTING-UP BACKGROUND IMAGE
# def setting_bg():
#     st.markdown(f""" <style>.stApp {{
#                         background: url("https://media.istockphoto.com/id/1308684522/vector/blue-and-green-blurred-motion-abstract-background.jpg?s=612x612&w=0&k=20&c=ELAPwLRDLH1AbjPDL9RyKBuJR9vcJqn0j8Iz4JLfuCI=");
#                         background-size: cover}}
#                      </style>""",unsafe_allow_html=True) 
# setting_bg()

# CREATING OPTION MENU
select = option_menu(None, ["Home","Upload & Extract","Modify","Contact"], 
                       icons=["house","cloud-upload","pencil-square","phone"],
                       default_index=0,
                       orientation="horizontal",
                       styles={"nav-link": {"font-size": "20px", "text-align": "centre", "margin": "0px", "--hover-color": "#6495ED"},
                               "icon": {"font-size": "20px"},
                               "container" : {"max-width": "6000px"},
                               "nav-link-selected": {"background-color": "#6495ED"}})

# INITIALIZING THE EasyOCR READER
reader = easyocr.Reader(['en'])

# CONNECTING WITH MYSQL DATABASE
mydb=mysql.connect(host="localhost",
                   user="root",
                   password="Pooventhiran2",
                   port="3306")
mycursor=mydb.cursor(buffered=True)

mycursor.execute("CREATE DATABASE if not exists BizCardX")
mycursor.execute("USE BizCardX")

# TABLE CREATION
mycursor.execute('''CREATE TABLE IF NOT EXISTS card_data(Id INTEGER PRIMARY KEY AUTO_INCREMENT,Card_holder TEXT,
                    Designation TEXT,Company_name TEXT,Mobile_number VARCHAR(50),Email TEXT,Website TEXT,Address TEXT,
                    Pin_code VARCHAR(100))''')

# HOME MENU
if select == "Home":
    col1,col2 = st.columns(2,gap="large")
    with col1:
        st.markdown("### :green[**Technologies Used :**] Python,easy OCR, Streamlit, SQL, Pandas")
        st.markdown("### :green[**Overview :**] In this streamlit web app you can upload an image of a business card and extract relevant information from it using easyOCR. You can view, modify or delete the extracted data in this app. This app would also allow users to save the extracted information into a database along with the uploaded business card image. The database would be able to store multiple entries, each with its own business card image and extracted information.")
    with col2:
        st.markdown("# ")
        st.markdown("# ")
        st.image(Image.open("C:/Users/poove/Downloads/Bizcard_img.png"),width=400)
        
        
# UPLOAD AND EXTRACT MENU
if select == "Upload & Extract":
    st.markdown("### Upload a Business Card")
    uploaded_card = st.file_uploader("upload here",label_visibility="collapsed",type=["png","jpeg","jpg"])
         
    if uploaded_card is not None:
        
        def save_card(uploaded_card):
            with open(os.path.join(uploaded_card.name), "wb") as f:
                f.write(uploaded_card.getbuffer())   
        save_card(uploaded_card)
        
        def image_preview(image,res): 
            for (bbox, text, prob) in res: 
              # unpack the bounding box
                (tl, tr, br, bl) = bbox
                tl = (int(tl[0]), int(tl[1]))
                tr = (int(tr[0]), int(tr[1]))
                br = (int(br[0]), int(br[1]))
                bl = (int(bl[0]), int(bl[1]))
                cv2.rectangle(image, tl, br, (0, 255, 0), 2)
                cv2.putText(image, text, (tl[0], tl[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            plt.rcParams['figure.figsize'] = (15,15)
            plt.axis('off')
            plt.imshow(image)
        
        # DISPLAYING THE UPLOADED CARD
        col1,col2 = st.columns(2,gap="large")
        with col1:
            st.markdown("#     ")
            st.markdown("#     ")
            st.markdown("### You have uploaded the card")
            st.image(uploaded_card)
        # DISPLAYING THE CARD WITH HIGHLIGHTS
        with col2:
            st.markdown("#     ")
            st.markdown("#     ")
            with st.spinner("Please wait processing image..."):
                st.set_option('deprecation.showPyplotGlobalUse', False)
                saved_img = os.getcwd()+  "\\" + uploaded_card.name
                image = cv2.imread(saved_img)
                res = reader.readtext(saved_img)
                st.markdown("### Image Processed and Data Extracted")
                st.pyplot(image_preview(image,res))  
                
            
        #easy OCR
        saved_img = os.getcwd()+ "\\" + uploaded_card.name
        result = reader.readtext(saved_img,detail = 0,paragraph=False)

        def img_to_binary(file):
            # Convert image data to binary format
            with open(file, 'rb') as file:
                binaryData = file.read()
            return binaryData
        
        def get_data(res):
            
            ext_dic = {'Name': [], 'Designation': [], 'Company name': [], 'Contact': [], 'Email': [], 'Website': [],
                    'Address': [], 'Pincode': []}

            ext_dic['Name'].append(result[0])
            ext_dic['Designation'].append(result[1])
            #ext_dic['Image'].append(img_to_binary(saved_img))

            for m in range(2, len(result)):
                if result[m].startswith('+') or (result[m].replace('-', '').isdigit() and '-' in result[m]):
                    ext_dic['Contact'].append(result[m])

                elif '@' in result[m] and '.com' in result[m]:
                    small = result[m].lower()
                    ext_dic['Email'].append(small)

                elif 'www' in result[m] or 'WWW' in result[m] or 'wwW' in result[m]:
                    small = result[m].lower()
                    ext_dic['Website'].append(small)

                elif 'TamilNadu' in result[m] or 'Tamil Nadu' in result[m] or result[m].isdigit():
                    ext_dic['Pincode'].append(result[m])

                elif re.match(r'^[A-Za-z]', result[m]):
                    ext_dic['Company name'].append(result[m])

                else:
                    removed_colon = re.sub(r'[,;]', '', result[m])
                    ext_dic['Address'].append(removed_colon)

            for key, value in ext_dic.items():
                if len(value) > 0:
                    concatenated_string = ' '.join(value)
                    ext_dic[key] = [concatenated_string]
                else:
                    value = 'NA'
                    ext_dic[key] = [value]

            return ext_dic
            
        #FUNCTION TO CREATE DATAFRAME
        df = pd.DataFrame.from_dict(get_data(result), orient='index')
        df = df.transpose()
        
        st.success("### Data Extracted!")
        st.write(df)
        
    if st.button("Upload to Database"):
        for i,row in df.iterrows():
                #here %S means string values 
            sql = """INSERT INTO card_data(Card_holder,Designation,Company_name,Mobile_number,Email,Website,Address,Pin_code)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
            mycursor.execute(sql, tuple(row))
                # the connection is not auto committed by default, so we must commit to save our changes
            mydb.commit()
        st.success("#### Uploaded to database successfully!")
        
# MODIFY MENU    
if select == "Modify":
    st.markdown("## Alter or Delete the data here")
    column1,column2 = st.columns(2,gap="large")
    with column1:
        mycursor.execute("SELECT card_holder FROM card_data")
        result = mycursor.fetchall()
        business_cards = {}
        for row in result:
            business_cards[row[0]] = row[0]
        selected_card = st.selectbox("Select a card holder name to update", list(business_cards.keys()))
        st.markdown("#### Update or modify any data below")
        mycursor.execute("select Card_holder,Designation,Company_name,Mobile_number,Email,Website,Address,Pin_code from card_data WHERE Card_holder=%s",
                        (selected_card,))
        result = mycursor.fetchone()

        # DISPLAYING ALL THE INFORMATIONS
        Company_name = st.text_input("Company_Name", result[2])
        Card_holder = st.text_input("Card_Holder", result[0])
        Designation = st.text_input("Designation", result[1])
        Mobile_number = st.text_input("Mobile_Number", result[3])
        Email = st.text_input("Email", result[4])
        Website = st.text_input("Website", result[5])
        Address = st.text_input("Address", result[6])
        Pin_code = st.text_input("Pin_Code", result[7])

        if st.button("Commit changes to DB"):
            # Update the information for the selected business card in the database
            mycursor.execute("UPDATE card_data SET Company_name=%s,Card_holder=%s,Designation=%s,Mobile_number=%s,Email=%s,Website=%s,Address=%s,Pin_code=%s\
                                WHERE Card_holder=%s", (Company_name,Card_holder,Designation,Mobile_number,Email,Website,Address,Pin_code,selected_card))
            mydb.commit()
            st.success("Information updated in database successfully.")

    with column2:
        mycursor.execute("SELECT Card_holder FROM card_data")
        result = mycursor.fetchall()
        business_cards = {}
        for row in result:
            business_cards[row[0]] = row[0]
        selected_card = st.selectbox("Select a card holder name to Delete", list(business_cards.keys()))
        st.write(f"### You have selected :green[**{selected_card}'s**] card to delete")
        st.write("#### Proceed to delete this card?")

        if st.button("Yes Delete Business Card"):
            mycursor.execute(f"DELETE FROM card_data WHERE card_holder='{selected_card}'")
            mydb.commit()
            st.success("Business card information deleted from database.")
    
    if st.button("View updated data"):
        mycursor.execute("select Company_name,Card_holder,Designation,Mobile_number,Email,Website,Address,Pin_code from card_data")
        updated_df = pd.DataFrame(mycursor.fetchall(),columns=["Company_Name","Card_Holder","Designation","Mobile_Number","Email","Website","Address","Pin_Code"])
        st.write(updated_df)

#----------------------Contact---------------#

if select == "Contact":
    Name = (f'{"Name :"}  {"Poovethiran M"}')
    mail = (f'{"Mail :"}  {"Pooventhiranmurukesan@gmail.com"}')
    social_media = {
        "GITHUB": "https://github.com/PooventhiranM/Phone_pe-pulse-data-visulaization.git",
        "LINKEDIN": "https://www.linkedin.com/in/pooventhiranmurukesan/"}
    
    col1, col2, col3 = st.columns(3)
    col3.image(Image.open("C:/Users/poove/OneDrive/Desktop/My documents/Pooven.jpg"), width=300)

    with col1:
        st.title('BizCardX: Extracting Business Card Data with OCR')
        st.write("The goal of this project is to extract data from the business card images, transform and clean the data, insert it into a MySQL database and update data in the database.")
        st.write("---")
        st.subheader(Name)
        st.subheader("An Aspiring DATA-SCIENTIST..!")
        st.subheader(mail)     
    st.write("#")
    with col3:
        st.write("#")
        st.write("#")
        st.write("#")
        st.write("#")
        for index, (platform, link) in enumerate(social_media.items()):
            st.write(f"[{platform}]({link})")
