import os
import json
import pickle
import time
import random
from matplotlib.pyplot import show
import streamlit as st
from streamlit_folium import st_folium
import folium
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from geopy.geocoders import Nominatim

# Настройка страницы в широком режиме
st.set_page_config(layout="wide")

# Файл для кеширования результатов геокодирования
CACHE_FILE = "./geocode_cache.json"

# Загружаем кеш, если файл существует, или создаем пустой словарь
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        geocode_cache = json.load(f)
else:
    geocode_cache = {}

# Функция для получения координат с использованием кеша
def get_geocode(query, geolocator, cache):
    if query in cache:
        st.write(f"Используется кеш для запроса: **{query}**")
        st.write(f"Координаты: {cache[query]['latitude']}, {cache[query]['longitude']}")
        return cache[query]
    else:
        time.sleep(1)  # задержка для соблюдения правил API
        try:
            location = geolocator.geocode(query, timeout=10)
            if location:
                result = {"latitude": location.latitude, "longitude": location.longitude}
                cache[query] = result
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump(cache, f, ensure_ascii=False, indent=2)
                return result
        except Exception as e:
            st.error(f"Ошибка при поиске {query}: {e}")
    return None

districts_en_el = {
    "Famagusta": "Αμμοχώστου", 
    "Larnaca" : "Λάρνακας", 
    "Limassol": "Λεμεσού", 
    "Nicosia" : "Λευκωσίας",
    "Paphos" : "Πάφος"
}

# Словарь с районами и списками деревень на Кипре
villages = {
    "Πάφος": [
        "Άγιος Γεώργιος",
        "Άγιος Δημητριανός",
        "Άγιος Ιωάννης",
        "Άγιος Νικόλαος",
        "Άρμου",
        "Έμπα",
        "Ίννια",
        "Αγία Μαρίνα Κελοκεδάρων",
        "Αγία Μαρίνα Χρυσοχούς",
        "Αγία Μαρινούδα",
        "Ακουρσός",
        "Αμαργέτη",
        "Αναδιού",
        "Αναρίτα",
        "Ανδρολύκου",
        "Αξύλου",
        "Αργάκα",
        "Αρμίνου",
        "Αρχιμανδρίτα",
        "Ασπρογιά",
        "Αχέλεια",
        "Γαλαταριά",
        "Γιόλου",
        "Γουδί",
        "Γυαλιά",
        "Δρούσια",
        "Δρυνιά",
        "Δρύμου",
        "Ελεδιώ",
        "Θελέτρα",
        "Κάθηκας",
        "Κάτω Ακουρδάλια",
        "Κάτω Αρόδες",
        "Κέδαρες",
        "Καλλέπεια",
        "Κανναβιού",
        "Κελοκέδαρα",
        "Κιδάσι",
        "Κινούσα",
        "Κισσόνεργα",
        "Κοίλη",
        "Κοιλίνια",
        "Κονιά",
        "Κούκλια",
        "Κούρτακα",
        "Κρήτου Μαρόττου",
        "Κρήτου Τέρρα",
        "Λάσα",
        "Λέμπα",
        "Λεμόνα",
        "Λετύμπου",
        "Λυσός",
        "Μέσα Χωριό",
        "Μέσανα",
        "Μακούντα",
        "Μαμώνια",
        "Μαραθούντα",
        "Μεσόγη",
        "Μηλιά",
        "Μηλιού",
        "Μούσερε",
        "Νέα Δήμματα",
        "Νέο Χωριό",
        "Νατά",
        "Νικόκλεια",
        "Πάνω Ακουρδάλια",
        "Πάνω Αρόδες",
        "Παναγιά",
        "Πελαθούσα",
        "Πενταλιά",
        "Πολέμι",
        "Πραιτώρι",
        "Πραστειό Κελοκεδάρων",
        "Πωμός",
        "Πόλη Χρυσοχούς",
        "Σίμου",
        "Σαλαμιού",
        "Σκούλλι",
        "Στατός / Άγιος Φώτιος",
        "Σταυροκόννου",
        "Στενή",
        "Στρουμπί",
        "Τάλα",
        "Τέρρα",
        "Τίμη",
        "Τραχυπέδουλα",
        "Τρεμιθούσα",
        "Τσάδα",
        "Φιλούσα Κελοκεδάρων",
        "Φιλούσα Χρυσοχούς",
        "Φοίτη",
        "Χλώρακα",
        "Χολέτρια",
        "Χούλου",
        "Χρυσοχού",
        "Χόλι",
        "Ψάθι"
    ],
    "Λευκωσίας": [
        "Άγιοι Τριμιθιάς",
        "Άγιος Γεώργιος Καύκαλλου",
        "Άγιος Επιφάνιος Ορεινής",
        "Άγιος Θεόδωρος Σολέας",
        "Άγιος Ιωάννης Μαλούντας",
        "Άλωνα",
        "Αγία Βαρβάρα",
        "Αγία Ειρήνη",
        "Αγία Μαρίνα Ξυλιάτου",
        "Αγροκήπια",
        "Ακάκι",
        "Αλάμπρα",
        "Αληθινού",
        "Ανάγυια",
        "Αναλιόντας",
        "Ανθούπολη Συνοικισμός",
        "Απλίκι",
        "Αρεδιού",
        "Ασκάς",
        "Αστρομερίτης",
        "Βυζακιά",
        "Γαλάτα",
        "Γερακιές",
        "Γούρρι",
        "Δένεια",
        "Επισκοπειό",
        "Εργάτες",
        "Ευρύχου",
        "Κάμπος",
        "Κάτω Δευτερά",
        "Κάτω Κουτραφάς",
        "Κάτω Μονή",
        "Κάτω Πύργος",
        "Κακοπετριά",
        "Καλλιάνα",
        "Καλοπαναγιώτης",
        "Καλό Χωριό Ορεινής",
        "Καμπί του Φαρμακά",
        "Καμπιά",
        "Καννάβια",
        "Καπέδες",
        "Κατύδατα",
        "Κλήρου",
        "Κοκκινοτριμιθιά",
        "Κοράκου",
        "Κοτσιάτης",
        "Κούρδαλι (Σπήλια)",
        "Λαγουδερά",
        "Λαζανιάς",
        "Λειβάδια Πιτσιλιάς",
        "Λινού",
        "Λυθροδόντας",
        "Λύμπια",
        "Μάμμαρι",
        "Μένοικο",
        "Μαθιάτης",
        "Μαλούντα",
        "Μαρκί",
        "Μηλικούρι",
        "Μιτσερό",
        "Μοσφίλι",
        "Μουτουλλάς",
        "Νήσου",
        "Νικητάρι",
        "Ξυλιάτος",
        "Οίκος",
        "Ορούντα",
        "Πάνω Δευτερά",
        "Πάνω Πύργος",
        "Πέρα Ορεινής",
        "Πέρα Χωριό",
        "Παλαιχώρι Μόρφου",
        "Παλαιχώρι Ορεινής",
        "Παλιομέτοχο",
        "Παχύαμμος",
        "Πεδουλάς",
        "Περιστερώνα",
        "Πηγαίνια",
        "Πλατανιστάσα",
        "Πολιτικό",
        "Πολύστυπος",
        "Ποτάμι",
        "Ποταμιά",
        "Σαράντι",
        "Σια",
        "Σινά Όρος",
        "Σπήλια – Αγίου Αντωνίου",
        "Τεμπριά",
        "Τσακκίστρα",
        "Φαρμακάς",
        "Φλάσου",
        "Φτερικούδι",
        "Φυκάρδου",
        "Ψημολόφου"
    ],
    "Λεμεσού": [
        "Άγιος Αμβρόσιος",
        "Άγιος Γεώργιος Συλίκου",
        "Άγιος Δημήτρης",
        "Άγιος Θεράπων",
        "Άγιος Θεόδωρος ",
        "Άγιος Θωμάς",
        "Άγιος Ιωάννης Πιτσιλιάς",
        "Άγιος Κωνσταντίνος",
        "Άγιος Μάμας",
        "Άγιος Παύλος",
        "Άγιος Τύχωνας",
        "Άλασσα",
        "Άρσος",
        "Όμοδος",
        "Αγρίδια",
        "Αγρός",
        "Ακαπνού",
        "Ακρούντα",
        "Ακρωτήρι",
        "Αλέκτορα",
        "Αμίαντος",
        "Ανώγυρα",
        "Απαισιά",
        "Αρακαπάς",
        "Αρμενοχώρι",
        "Ασγάτα",
        "Ασώματος",
        "Αυδήμου",
        "Αψιού",
        "Βάσα Κελλακίου",
        "Βάσα Κοιλανίου",
        "Βίκλα",
        "Βουνί",
        "Γεράσα",
        "Γεροβάσα/Τρόζενα",
        "Διερώνα",
        "Δορά",
        "Δωρός",
        "Δύμες",
        "Επισκοπή",
        "Επταγώνια",
        "Ερήμη",
        "Ζωοπηγή",
        "Κάτω Κυβίδες",
        "Κάτω Μύλος",
        "Κάτω Πλάτρες",
        "Καλό Χωριό  ",
        "Καμινάρια",
        "Καντού",
        "Καπηλειό",
        "Κελλάκι",
        "Κισσούσα",
        "Κλωνάρι",
        "Κοιλάνι",
        "Κολόσσι",
        "Κορφή",
        "Κουκά",
        "Κυπερούντα",
        "Λάνια",
        "Λεμύθου",
        "Λιμνάτης",
        "Λουβαράς",
        "Λόφου",
        "Μαθηκολώνη",
        "Μαλλιά",
        "Μανδριά",
        "Μονάγρι",
        "Μονή",
        "Μοναγρούλλι",
        "Μονιάτης",
        "Μουτταγιάκα",
        "Πάνω Κυβίδες",
        "Πάνω Πλάτρες",
        "Πάνω Πολεμίδια ",
        "Πάρα Πεδί",
        "Πάχνα",
        "Παλιόμυλος",
        "Παλώδια",
        "Παραμάλι",
        "Παραμύθα",
        "Παρεκκλησιά",
        "Πελένδρι",
        "Πεντάκωμο",
        "Πισσούρι",
        "Πλατανίσκια",
        "Ποταμίτισσα",
        "Ποταμιού",
        "Πραστειό",
        "Πραστειό Αυδήμου",
        "Πραστειό Κελλακίου",
        "Πρόδρομος",
        "Πύργος",
        "Σανίδα",
        "Σούνι Ζανατζιά",
        "Σπιτάλι",
        "Συκόπετρα",
        "Συλίκου",
        "Σωτήρα",
        "Τραχώνι",
        "Τρεις Εληές",
        "Τριμίκλινη",
        "Τσερκέζ Τσιφλίκ",
        "Φασούλα",
        "Φοινί",
        "Φοινικάρια",
        "Χανδριά"
    ],
    "Λάρνακας": [
        "Αγίοι Βαβατσινιάς",
        "Άγιος Θεόδωρος",
        "Αβδελλερό",
        "Αγία Άννα",
        "Αγγλισίδες",
        "Αλαμινός",
        "Αλεθρικό",
        "Αναφωτία",
        "Βάβλα",
        "Βαβατσινιά",
        "Δελίκηπος",
        "Ζύγι",
        "Κάτω Δρυς",
        "Κάτω Λεύκαρα",
        "Κίτι",
        "Καλαβασός",
        "Καλό Χωριό",
        "Κελλιά",
        "Κιβισίλι",
        "Κλαυδιά",
        "Κοφίνου",
        "Κόρνος",
        "Λάγια",
        "Μαζωτός",
        "Μαρί",
        "Μαρώνι",
        "Μελίνη",
        "Μεννόγεια",
        "Μοσφιλωτή",
        "Ξυλοτύμπου",
        "Ξυλοφάγου",
        "Οδού",
        "Ορά",
        "Ορμήδεια",
        "Ορόκλινη",
        "Περβόλια",
        "Πυργά",
        "Πύλα",
        "Σκαρίνου",
        "Τερσεφάνου",
        "Τρούλλοι",
        "Τόχνη",
        "Χοιροκοιτία",
        "Ψεματισμένος",
        "Ψευδάς"
    ],
    "Αμμοχώστου": [
        "Άγιος Γεώργιος Αχερίτου",
        "Άχνα",
        "Αυγόρου",
        "Λιοπέτρι",
        "Φρέναρος"
    ]
}
clicked_district = None
isDialog = False

# Загружаем или создаем список вопросов (вопрос = словарь с деревней и правильным дистриктом)
QUESTIONS_FILE = "./questions.pickle"
if os.path.exists(QUESTIONS_FILE):
    with open(QUESTIONS_FILE, "rb") as f:
        questions = pickle.load(f)
else:
    questions = []
    for district, village_list in villages.items():
        for village in village_list:
            questions.append({"village": village, "district": district})
    random.shuffle(questions)
    with open(QUESTIONS_FILE, "wb") as f:
        pickle.dump(questions, f)

# Сохраняем вопросы в session_state, если еще не сохранены
if "questions" not in st.session_state:
    st.session_state.questions = questions
    st.session_state.question_index = 0
    st.session_state.score = 0
st.title("Викторина: Найди дистрикт для деревни")

# Сайдбар для выбора размеров карты (адаптивность)
map_width = 500
map_height = 500

# ... (предыдущий код без изменений)

@st.dialog("Answer")
def show_answer(clicked_district):
    st.markdown(
        """
        <style>
        /* Скрываем кнопку закрытия диалога (крестик) */
        div[aria-label="dialog"] > button[aria-label="Close"] {
            display: none;
        }
        /* Отключаем клики по затемненному фону (оверлею) */
        div[data-baseweb="modal"] {
            pointer-events: none !important;
        }
        /* Обеспечиваем, чтобы само диалоговое окно оставалось кликабельным */
        div[aria-label="dialog"] {
            pointer-events: auto;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    current_question = st.session_state.questions[st.session_state.question_index]
    
    st.write(f"Вы выбрали дистрикт: **{clicked_district}**")
    
    # Проверяем правильность ответа
    if districts_en_el.get(clicked_district.strip(), "").lower() == current_question["district"].strip().lower():
        st.success(f"✅ Правильно! {current_question["district"].strip().lower()}" )
        st.session_state.score += 1
    else:
        st.error(f"❌ Неверно. Правильный ответ: **{current_question['district']}**")
        
    # Кнопка для следующего вопроса
    if st.button("Следующий вопрос", key=f"next_{st.session_state.question_index}"):
        # Сбрасываем состояние диалога и клика
        st.session_state.question_index += 1
        st.session_state.isDialog = False
        if "last_clicked" in st.session_state:
            del st.session_state.last_clicked
        st.rerun()


if st.session_state.question_index < len(st.session_state.questions):
    current_question = st.session_state.questions[st.session_state.question_index]
    st.header(f"Вопрос {st.session_state.question_index+1}: {current_question['village']}")
    
    # Создание карты
    m = folium.Map(location=[35.0, 33.0], zoom_start=8.4)
    SHAPEFILE_PATH = "./cyprus_Districts_level_1.shp"
    cyprus_gdf = gpd.read_file(SHAPEFILE_PATH)
    folium.GeoJson(cyprus_gdf.to_json()).add_to(m)
    
    # Обработка кликов
    map_data = st_folium(m, width=map_width, height=map_height, key=f"map_{st.session_state.question_index}")
    
    if map_data.get("last_clicked") and not st.session_state.get("isDialog"):
        # Сохраняем информацию о клике в session_state
        st.session_state.last_clicked = map_data["last_clicked"]
        st.session_state.last_active_drawing = map_data["last_active_drawing"]
        
        # Определяем выбранный дистрикт
        clicked_district = st.session_state.last_active_drawing["properties"]["shape1"]
        st.session_state.isDialog = True
        show_answer(clicked_district)

else:
    st.success(f"🎉 Викторина завершена! Правильных ответов: {st.session_state.score}/{len(questions)}")