import plotly.express as px
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

# Konfigurasi awal streamlit
st.set_page_config(
    page_title = 'FSB - Final Project', 
    page_icon = '🐧', 
    layout = "wide"
)

# Pembacaan teks 
def read_text(filename):
    with open(filename) as file:
        grades = file.read()
    return(grades)

# Ekstrak data & cleansing
@st.cache_resource
def ekstrak_data():
    #Ekstraksi data
    raw_data = pd.read_csv('D:/Full Stack Bangalore/telecom_customer_churn.csv')

    # Copy data ke variabel baru
    data = raw_data.copy()
    
    # Transformasi nama kolom menjadi lowercase
    data.columns = data.columns.str.lower()
    data.columns = data.columns.str.replace(' ', '_')

    # Drop some columns
    data = data.drop(columns = ['zip_code',	'latitude',	'longitude'])

    return (data)

# Ornamen pada header
def header():
    spacer1, row1, spacer2 = st.columns([0.1, 7.2, 0.1])
    
    row1.title('Telco Churn Analysis')
    row1.subheader('Streamlit App by [Bachtiyar M. Arief](https://www.linkedin.com/in/bachtiyarma/)')
    
    row1.header('Latar Belakang')
    
    teks_header = read_text('D:/Full Stack Bangalore/1. Abstrak.txt')
    row1.markdown(
        teks_header, 
        unsafe_allow_html = True
    )
        
def tampilkan_data(data):
    spacer1, row1, spacer2 = st.columns([0.1, 7.2, 0.1])
    row1.header('Data')
    row1.markdown(
        'Data yang digunakan pada proyek ini disajikan dalam tabel berikut',
        unsafe_allow_html = True
    )
    
    spacer1, row2, row3, spacer2 = st.columns([0.1, 7.2, 7.2, 0.1])
    row2.metric(
        label = "Total Data", 
        value = data.shape[0]
    )
        
    row3.metric(
        label = "Total Kolom", 
        value = data.shape[1]
    )
    
    spacer1, row4, spacer2 = st.columns([0.1, 7.2, 0.1])
    row4.dataframe(data)

# Hitung banyak customer yang dikelompokkan berdasarkan status
def perhitungan_customer_status(data):
    # Hitung total data (unik) customer id per status customernya
    cust_status = data.groupby(['customer_status'], as_index = False).agg(total_cust_status = ('customer_id', pd.Series.nunique))

    # Buat grafik pie
    fig = px.pie(
        cust_status, 
        values = 'total_cust_status', 
        names = 'customer_status',
        #hover_data = ['total_cust_status'], 
        labels = {
            'customer_status' : 'Customer Status',
            'total_cust_status' : 'Total Customer'
        },
        color = 'customer_status',
        color_discrete_map = {
            'Churned' : '#ff0000',
            'Stayed' : '#5bb450',
            'Joined' : '#72bf6a'                                 
        }
    )

    fig.update_traces(
        textposition = 'inside', 
        textinfo = 'percent+label',
        pull = [0.1, 0, 0]
    )


    fig.update_layout(
        autosize = False,
        width = 400,
        height = 450,
        showlegend = False,
        plot_bgcolor = 'rgba(0, 0, 0, 0)',
        paper_bgcolor = 'rgba(0, 0, 0, 0)'
    )

    return (cust_status, fig)

def tampilkan_status_customer(data):
    
    spacer1, row1, spacer2 = st.columns([0.1, 7.2, 0.1])
    row1.header('Gambaran Awal')
    
    spacer1, row1, spacer2, row2, spacer3 = st.columns([0.1, 4, 0.1, 3.2, 0.1])
    cust_status, fig = perhitungan_customer_status(data)
    
    total_cust_churn = cust_status[cust_status['customer_status'] == 'Churned']['total_cust_status'].values[0]
    total_joined_churn = cust_status[cust_status['customer_status'] == 'Joined']['total_cust_status'].values[0]
    total_stay_churn = cust_status[cust_status['customer_status'] == 'Stayed']['total_cust_status'].values[0]
    
    row1.plotly_chart(
        fig, 
        use_container_width = False
    )
    
    row2.markdown(f"""
        Pada grafik Pie disamping, diperoleh fakta bahwa sebanyak <b>{total_cust_churn}</b> 
        customer tidak lagi melanjutkan berlangganan (<i>Churned</i>),
        <b>{total_stay_churn}</b> customer masih aktif berlangganan (<i>Stayed</i>) 
        dan untuk periode ini perusahaan berhasil memperoleh <b>{total_joined_churn}</b> customer baru (<i>Joined</i>).
        <br><br>
        
        Jika diamati, proporsi customer yang <i>churned</i> lebih besar daripada proporsi customer baru (<i>joined</i>) yang didapatkan. 
        Sehingga perlu bagi perusahaan untuk mengetahui dari data yang ada faktor apa saja yang menyebabkan customer menghentikan
        berlangganan pada perusahaan dan perlu segera menetapkan strategi lebih lanjut untuk meretensi customer yang masih berlangganan dan
        meningkatkan jumlah customer baru.
        """,
        unsafe_allow_html = True                               
    )

def perhitungan_churn_reason(data):
    
    # Hitung total data cust
    cust_churn_category = data.groupby(['churn_category', 'churn_reason'], as_index = False).agg(total_cust_churn_per_reason = ('customer_id', pd.Series.nunique))

    cust_churn_category['total_cust_churn_per_category'] = cust_churn_category.groupby(['churn_category'], as_index = False)['total_cust_churn_per_reason'].transform(sum)

    cust_churn_category = cust_churn_category.sort_values(
        by = ['total_cust_churn_per_category', 'total_cust_churn_per_reason'], 
        ascending = True,
        ignore_index = True
    )
    
    cust_churn_category['index_largest'] = cust_churn_category.sort_values(['total_cust_churn_per_reason'], ascending = False) \
             .groupby(['churn_category']) \
             .cumcount() + 1
             
    cust_churn_category['index_largest'] = ['largest' if x == 1 else '' for x in cust_churn_category['index_largest']]
    cust_churn_category['text'] = cust_churn_category['churn_reason'] + '<br> (' + cust_churn_category['total_cust_churn_per_reason'].astype(str) + ')'

    fig = px.bar(
        cust_churn_category, 
        x = "total_cust_churn_per_reason", 
        y = "churn_category", 
        color = "index_largest", 
        color_discrete_map = {
            'largest' : '#FF0000',
            '' : '#F4b4b4'
        },
        orientation = 'h',
        text = "text",
    )

    fig.update_layout(
        autosize = False,
        width = 650,
        height = 400,
        showlegend = False,
        xaxis=dict(
            title = "",
            zeroline=False,
            showgrid = False,
            side = 'top'
        ),
        yaxis=dict(
            title = '',
            visible = True, 
            showticklabels = True,
            showgrid = False
        ),
        font = dict(
            size = 9
        ),
        plot_bgcolor = 'rgba(0, 0, 0, 0)',
        paper_bgcolor = 'rgba(0, 0, 0, 0)'
    )

    hovertemplate = '<b>%{y}</b><br>'\
                    '%{text}<br>'
                    
    fig.update_traces(
        hovertemplate = hovertemplate, 
        customdata = cust_churn_category["churn_reason"]
    )

    return(cust_churn_category, fig)

def tampilkan_alasan_churn(data):
    spacer1, row1, spacer2 = st.columns([0.1, 7.2, 0.1])
    row1.header('Alasan Customer Churn?')
    
    spacer1, row1, row2 = st.columns([0.1, 5, 6])
    cust_churn_category, fig = perhitungan_churn_reason(data)
    
    row1.markdown(f"""
       <br>Dari hasil penelusuran, ternyata alasan terbesar banyak customer berpindah haluan dari perusahaan adalah
       karena Kompetitor. Lebih spesifik ternyata perusahaan kompetitor ternyata memiliki device atau teknologi 
       yang lebih baik / canggih. Alasan berikutnya berkorelasi dengan alasan utama pelanggan churn yakni ketidakpuasan
       pelanggan terhadap produk perusahaan yang disajikan. Dengan demikian perusahaan harus melakukan evaluasi terkait
       produk layanan dan menganalisa produk dari kompetitor yang menarik customer. Tidak hanya dari sisi produk yang
       perlu di upgrade, pelayanan lain seperti mengevaluasi sikap dan kinerja karyawan, melakukan promo dan alasan lainnya
       juga harus menjadi perhatian perusahaan jika ingin mempertahankan customer lebih baik kedepannya.
        """,
        unsafe_allow_html = True                               
    )
    
    row2.plotly_chart(
        fig, 
        use_container_width = False
    )
     
def text_graph(text1, text2, color):
    fig, [ax1, ax2] = plt.subplots(
        nrows = 2, 
        ncols = 1,
        figsize = (1, 0.5)
    )

    ax1.text(
        x = 0, 
        y = 0.2, 
        s = text1,
        color = color,
        fontsize = 14,
        fontweight = 'light',
    )

    ax2.text(
        x = 0, 
        y = 0.1, 
        s = text2,
        color = color,
        fontsize = 18,
        fontweight = 'semibold',
    )

    ax1.axis('off')
    ax2.axis('off')
    
    return fig 

def tampilkan_revenue_impact(data):
    # Hitung total data (unik) customer id per status customernya
    revenue_per_status = data.groupby(['customer_status'], as_index = False).agg(total_revenue = ('total_revenue', pd.Series.sum))

    raw_revenue_stayed = revenue_per_status[revenue_per_status['customer_status'] == 'Stayed']['total_revenue'].values[0] 
    raw_revenue_joined = revenue_per_status[revenue_per_status['customer_status'] == 'Joined']['total_revenue'].values[0]
    raw_revenue_churn = revenue_per_status[revenue_per_status['customer_status'] == 'Churned']['total_revenue'].values[0]

    revenue_stayed = round(raw_revenue_stayed / 10**6, 2)
    revenue_joined = round(raw_revenue_joined / 10**6, 2)
    revenue_churn = round(raw_revenue_churn / 10**6, 2)
    
    fig1 = text_graph('Stayed', '$ ' + str(revenue_stayed) + 'M', '#5bb450')
    fig2 = text_graph('Joined', '$ ' + str(revenue_joined) + 'M', '#5bb450')
    fig3 = text_graph('Churn', '$ ' + str(revenue_churn) + 'M', '#ff0000')
    
    spacer1, row1, spacer2 = st.columns([0.1, 7.2, 0.1])
    row1.header('Dampak Terhadap Perusahaan')
    
    spacer1, row2, row3, row4, spacer2 = st.columns([0.1, 3, 3, 3, 0.1])
    
    row2.pyplot(
        fig1, 
        use_container_width = False
    )
    
    row3.pyplot(
        fig2, 
        use_container_width = False
    )
    
    row4.pyplot(
        fig3, 
        use_container_width = False
    )
    
    spacer1, row5, spacer2 = st.columns([0.1, 7.2, 0.1])
    row5.markdown(f"""
        Dampak customer saat memutuskan untuk tidak lagi berlangganan dengan perusahaan adalah dapat dengan jelas terlihat bahwa perusahaan merugi sebesar 
        \${revenue_churn}M (lebih detail = \${round(raw_revenue_churn, 2)}). Hal ini menjadi perhatian perusahaan dikarenakan jumlah kerugian karena customer yang churned di
        bandingkan dengan jumlah pendapatan baru yang diperoleh perusahaan yakni sebesar \${revenue_joined}M (lebih detail = \${round(raw_revenue_joined, 2)}).
        Sehingga dengan melihat ketakseimbangan pendapatan yang terjadi perlu menjadi perhatian besar terkait penyebab customer tidak lagi berlangganan, sehingga dampak yang
        lebih besar yang mungkin akan terjadi dapat diminimalkan resikonya.
        """, 
        unsafe_allow_html = True)

# All Demografi
def img_to_html(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    img_html = "<img src='data:image/png;base64,{}' class='img-fluid' width='250' height='250'>".format(
      encoded
    )
    return img_html

def count_per_gender(data):
    count_data_per_gender = data.groupby(['gender'], as_index = False).agg(count_data_per_gender = ('customer_id', pd.Series.nunique))
    count_male_data = count_data_per_gender[count_data_per_gender['gender'] == 'Male']['count_data_per_gender'].values[0]
    count_female_data = count_data_per_gender[count_data_per_gender['gender'] == 'Female']['count_data_per_gender'].values[0]
    return (count_male_data, count_female_data)

def distribusi_umur(data, gender, color):
    fig = px.histogram(
        data[data['gender'] == gender], 
        x = "age",
        nbins = 10,
        color_discrete_sequence=[color]
    )

    fig.update_layout(
        autosize = False,
        width = 500,
        height = 400,
        bargap = 0.02,
        showlegend = False,
        xaxis = dict(
            title = "age",
            zeroline=False,
            showgrid = False
        ),
        yaxis = dict(
            title = "",
            visible = True, 
            showticklabels = True,
            showgrid = False
        ),
        font = dict(
            size=9
        ),
        plot_bgcolor = 'rgba(0, 0, 0, 0)',
        paper_bgcolor = 'rgba(0, 0, 0, 0)'
    )

    return fig

def married_status(data, gender, color):
    married_per_gender = data[data['gender'] == gender].groupby(['married'], as_index = False).agg(married_per_gender = ('customer_id', pd.Series.nunique))

    fig = px.pie(
        married_per_gender, 
        values = 'married_per_gender', 
        names = 'married',
        labels = {
            'married' : 'is Married?',
            'married_per_gender' : 'Total Customer'
        },
        color = 'married',
        color_discrete_map = {
            'Yes' : color[0],
            'No' : color[1]                                
        },
        hole = 0.5
    )

    fig.update_traces(
        textposition = 'inside', 
        textinfo = 'percent+label',
        pull = [0.01, 0]
    )


    fig.update_layout(
        autosize = False,
        width = 500,
        height = 400,
        showlegend = False,
        plot_bgcolor = 'rgba(0, 0, 0, 0)',
        paper_bgcolor = 'rgba(0, 0, 0, 0)'
    )
    
    return (fig)

    
def tampilkan_demografi(data):
    male_color, female_color = '#fbe280', '#5bbc95'
    
    spacer1, row1, spacer2 = st.columns([0.1, 7.2, 0.1])
    row1.header('Demografi Customer Berdasarkan Status')
    status = row1.multiselect(
        label = 'Pilih Status Customers',
        options = data['customer_status'].unique(),
        default = 'Churned'
    )
    
    filter_data = data.loc[data['customer_status'].isin(status)]

    count_male_data, count_female_data = count_per_gender(filter_data)
    fig_hist_male = distribusi_umur(filter_data, gender = 'Male', color = male_color)
    fig_hist_female = distribusi_umur(filter_data, gender = 'Female', color = female_color)

    fig_pie_married_male = married_status(filter_data, gender = 'Male', color = ('#bfac60', male_color))
    fig_pie_married_female = married_status(filter_data, gender = 'Female', color = ('#469173', female_color))
    
    spacer1, row2, spacer, row3, spacer3 = st.columns([0.1, 3, 0.5, 3, 0.1])
    row2.markdown(
        f"<p style='text-align: center; color: {male_color}; font-size : 350%;'> Male </p>", 
        unsafe_allow_html = True
    )
    
    row2.markdown(
        "<p style='text-align: center;'>" + img_to_html('D:\Full Stack Bangalore\man.png') + "</p>", 
        unsafe_allow_html = True
    )
    
    row2.markdown(
        f"<p style='text-align: center; color: {male_color}; font-size : 350%;'> {count_male_data} </p>", 
        unsafe_allow_html = True
    )
    
    row2.markdown(
        f"<p style='text-align: center; color: {male_color}; font-size : 150%;'> ({', '.join(status)}) </p>", 
        unsafe_allow_html = True
    )
    
    row2.plotly_chart(
        fig_hist_male, 
        use_container_width = False
    )
    row2.plotly_chart(
        fig_pie_married_male, 
        use_container_width = False
    )
    
    row3.markdown(
        f"<p style='text-align: center; color: {female_color}; font-size : 350%;'> Female </p>", 
        unsafe_allow_html = True
    )
    row3.markdown(
        "<p style='text-align: center;'>" + img_to_html('D:\Full Stack Bangalore\woman.png') + "</p>", 
        unsafe_allow_html = True
    )
    row3.markdown(
        f"<p style='text-align: center; color: {female_color}; font-size : 350%;'> {count_female_data} </p>", 
        unsafe_allow_html = True
    )
    row3.markdown(
        f"<p style='text-align: center; color: {female_color}; font-size : 150%;'> ({', '.join(status)}) </p>", 
        unsafe_allow_html = True
    )

    row3.plotly_chart(
        fig_hist_female, 
        use_container_width = False
    )
    
    row3.plotly_chart(
        fig_pie_married_female, 
        use_container_width = False
    )
    
    
if __name__ == "__main__":
    header()
    
    data = ekstrak_data()
    
    tampilkan_data(data)
    tampilkan_status_customer(data)
    tampilkan_alasan_churn(data)
    tampilkan_revenue_impact(data)
    tampilkan_demografi(data)
