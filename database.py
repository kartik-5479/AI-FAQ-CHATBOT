"""
Database initialization and management module for Jarvis Chatbot
Handles SQLite database setup and operations
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = 'database.db'

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database with required tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # FAQs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL UNIQUE,
            answer TEXT NOT NULL,
            category TEXT NOT NULL,
            keywords TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Chat History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_question TEXT NOT NULL,
            bot_answer TEXT NOT NULL,
            confidence REAL,
            intent TEXT,
            faq_id INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (faq_id) REFERENCES faqs(id)
        )
    ''')
    
    # Favorites Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            user_question TEXT NOT NULL,
            bot_answer TEXT NOT NULL,
            date_saved TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES chat_history(id)
        )
    ''')
    
    # Statistics Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_questions INTEGER DEFAULT 0,
            total_conversations INTEGER DEFAULT 0,
            avg_confidence REAL DEFAULT 0,
            most_asked_category TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def insert_sample_faqs():
    """Insert 50+ sample FAQs into the database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if FAQs already exist
    cursor.execute('SELECT COUNT(*) FROM faqs')
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    sample_faqs = [
        # Admissions (5)
        ("What are the admission requirements?", "To apply, you need a valid high school diploma or equivalent, minimum GPA of 3.0, and a completed application form.", "Admissions", "admission requirements diploma GPA"),
        ("What is the application deadline?", "The application deadline is typically March 31st for fall admissions and October 31st for spring admissions.", "Admissions", "deadline application dates"),
        ("How much is the application fee?", "The application fee is $75 USD. This fee is non-refundable.", "Admissions", "application fee cost"),
        ("Do you offer scholarship programs?", "Yes, we offer merit-based, need-based, and athletic scholarships. Visit our financial aid office for more details.", "Admissions", "scholarship program financial aid"),
        ("What documents do I need to submit?", "You need transcripts, application form, essay, recommendation letters, and standardized test scores.", "Admissions", "documents required submission"),
        
        # Tourist Places in India (5)
        ("What are the best tourist places in India?", "Popular tourist destinations include Taj Mahal, Jaipur, Kerala, Goa, Varanasi, Agra, and the Himalayan regions. Each offers unique cultural and natural experiences.", "Tourist Places in India", "tourist places destinations attractions"),
        ("How should I visit Taj Mahal?", "The Taj Mahal is located in Agra. It's best to visit early morning or at sunset. You can hire a guide and purchase tickets at the entrance.", "Tourist Places in India", "Taj Mahal Agra visit"),
        ("What is the best time to visit Kerala?", "The best time to visit Kerala is from June to August (monsoon) and November to March (winter). This is when the weather is pleasant.", "Tourist Places in India", "Kerala weather season best time"),
        ("Are there beaches in Goa?", "Yes, Goa has beautiful beaches like Palolem Beach, Arambol Beach, and Baga Beach. They're perfect for swimming, sunbathing, and water sports.", "Tourist Places in India", "Goa beaches Palolem"),
        ("How do I reach Varanasi?", "You can reach Varanasi by air, train, or bus. The nearest airport is Lal Bahadur Shastri Airport. Trains and buses connect to major Indian cities.", "Tourist Places in India", "Varanasi transport reach"),
        
        # Courses (5)
        ("What courses do you offer?", "We offer undergraduate and postgraduate courses in Engineering, Business, Arts, Science, Medicine, and Law.", "Courses", "course list offerings programs"),
        ("Can I change my course after admission?", "Course changes are allowed within the first semester with valid reasons and departmental approval.", "Courses", "change course switch major"),
        ("What is the course duration?", "Undergraduate courses are typically 4 years, while postgraduate programs are 1-2 years depending on the specialization.", "Courses", "course duration length years"),
        ("Are online courses available?", "Yes, we offer online learning options for selected programs through our virtual learning platform.", "Courses", "online courses distance learning"),
        ("Which course has the highest placement rate?", "Engineering and MBA programs have the highest placement rates at 98% and 95% respectively.", "Courses", "placement rate highest"),
        
        # Fees (5)
        ("What is the annual fee structure?", "Annual fees range from $12,000 to $25,000 depending on the program. Please check the official fee schedule for details.", "Fees", "fees cost annual tuition"),
        ("When are fees due?", "Fees are typically due before the start of each semester. Payment plans are available.", "Fees", "due date fees payment deadline"),
        ("Is there a late fee?", "Yes, a 5% late fee is charged if fees are not submitted by the deadline.", "Fees", "late fee penalty"),
        ("Can I get a fee waiver?", "Fee waivers are available for economically disadvantaged students. Apply through the financial aid office.", "Fees", "fee waiver scholarship"),
        ("What payment methods are accepted?", "We accept online transfers, credit/debit cards, checks, and installment plans.", "Fees", "payment methods accepted"),
        
        # Library (5)
        ("What are the library hours?", "The library is open Monday-Friday 8 AM to 10 PM, Saturday 10 AM to 8 PM, and Sunday 12 PM to 8 PM.", "Library", "library hours open close"),
        ("How many books are in the library?", "Our library has over 500,000 books and 1000+ online journals in its collection.", "Library", "books collection size"),
        ("Can I borrow books online?", "Yes, we offer e-books and digital borrowing through our online library portal.", "Library", "online books e-books borrowing"),
        ("What is the book borrowing limit?", "Students can borrow up to 10 books at a time for a period of 2 weeks.", "Library", "borrowing limit books"),
        ("Is there a fine for late returns?", "Yes, a fine of $0.50 per day is charged for overdue books.", "Library", "fine overdue late return"),
        
        # Examinations (5)
        ("When are exams scheduled?", "Exams are typically scheduled at the end of each semester. The exact dates are announced 3 months in advance.", "Examinations", "exam schedule dates timing"),
        ("Can I apply for exam postponement?", "Yes, you can apply for postponement with valid reasons like medical emergency or family issues.", "Examinations", "postponement exam defer"),
        ("What is the exam pass percentage?", "The passing percentage is 40% for most subjects. Some advanced courses require 50%.", "Examinations", "pass percentage marks required"),
        ("Can I take exam makeup?", "Yes, makeup exams are available for students who miss exams due to valid reasons.", "Examinations", "makeup exam retake"),
        ("How long does result take after exam?", "Results are typically declared within 20-30 days after the final exam.", "Examinations", "result declaration time"),
        
        # Hostel (5)
        ("What is the hostel fee?", "Hostel fees are $3,000 to $5,000 per year depending on room type (single, double, or triple occupancy).", "Hostel", "hostel fee cost accommodation"),
        ("Can I apply for hostel accommodation?", "Yes, hostel accommodation is available for both local and international students on a first-come-first-served basis.", "Hostel", "hostel accommodation apply"),
        ("What facilities are available in the hostel?", "Facilities include wifi, 24-hour security, mess, laundry, gymnasium, and recreation areas.", "Hostel", "hostel facilities amenities"),
        ("Can I get a single room in the hostel?", "Single rooms are available but limited. Priority is given based on academic merit and seniority.", "Hostel", "single room hostel"),
        ("What are the hostel rules?", "Key rules include curfew at 10 PM on weekdays, no visitors after 8 PM, and maintenance of cleanliness.", "Hostel", "hostel rules regulations"),
        
        # Placements (5)
        ("What is the average salary offered?", "The average package offered is $40,000 to $80,000 per annum depending on specialization.", "Placements", "salary package average"),
        ("Which companies visit for campus recruitment?", "Top companies like Google, Microsoft, Amazon, Infosys, and TCS regularly visit for recruitment.", "Placements", "companies recruitment campus"),
        ("What is the placement percentage?", "Our overall placement rate is 96% with 100% placement in engineering programs.", "Placements", "placement percentage rate"),
        ("How can I improve my placement chances?", "Focus on academics, develop technical skills, participate in internships, and build a strong portfolio.", "Placements", "placement chances improve tips"),
        ("When does placement season start?", "Placement season typically starts in August and continues through December.", "Placements", "placement season timing"),
        
        # Faculty (5)
        ("How many faculty members are there?", "We have 500+ faculty members, including visiting professors and adjunct instructors.", "Faculty", "faculty members count number"),
        ("What are the faculty qualifications?", "Most faculty members hold Ph.D. degrees and have industry experience in their respective fields.", "Faculty", "faculty qualifications credentials"),
        ("Can I meet my professor during office hours?", "Yes, professors have fixed office hours. Check the course syllabus for schedule.", "Faculty", "office hours meeting professor"),
        ("How do I address my professor?", "Use formal titles like 'Prof. Dr. [Name]' or 'Dr. [Name]' unless instructed otherwise.", "Faculty", "professor address formal"),
        ("Are faculty members mentors for projects?", "Yes, faculty members actively mentor student projects and research initiatives.", "Faculty", "mentor faculty projects"),
        
        # Technical Support (5)
        ("Who should I contact for technical issues?", "Contact the IT Help Desk at support@university.edu or visit Room 102, Tech Building.", "Technical Support", "technical support help IT"),
        ("What is the response time for IT support?", "Critical issues are resolved within 2 hours. Non-critical issues typically within 24 hours.", "Technical Support", "response time IT support"),
        ("How do I reset my password?", "Visit the login page, click 'Forgot Password', and follow the reset instructions sent to your email.", "Technical Support", "password reset"),
        ("Is there a VPN available?", "Yes, students can download and install the university VPN from the IT portal.", "Technical Support", "VPN download access"),
        ("What should I do if my account is locked?", "Contact the IT Help Desk with valid identification. Account unlock typically takes 24 hours.", "Technical Support", "account locked unlock"),
        
        # General Information (5)
        ("What is the university ranking?", "Our institution is ranked #45 nationally and #200 globally for academic excellence.", "General Information", "ranking university position"),
        ("When was the university founded?", "The university was founded in 1950 and has over 70 years of educational excellence.", "General Information", "founded history establishment"),
        ("How many students are enrolled?", "Currently, we have 35,000+ students including 5,000+ international students.", "General Information", "student enrollment numbers"),
        ("What is the campus size?", "The main campus spans 500 acres with modern facilities and green spaces.", "General Information", "campus size area"),
        ("Are there sports facilities?", "Yes, we have state-of-the-art sports facilities including stadium, swimming pool, and gymnasium.", "General Information", "sports facilities recreation"),
        
        # Cooking & Recipes (10)
        ("How do I make a perfect biryani?", "Cook basmati rice, marinate chicken in yogurt and spices, layer with rice, and cook with ghee. Total time: 45 minutes.", "Cooking", "biryani recipe cooking"),
        ("What are healthy cooking tips?", "Use olive oil, include vegetables, reduce salt and sugar, cook at lower temperatures, and avoid deep frying.", "Cooking", "healthy cooking tips nutrition"),
        ("How long should I cook pasta?", "Generally cook pasta for 8-12 minutes depending on thickness. Taste to check for firmness.", "Cooking", "pasta cooking time"),
        ("What's the best way to cook chicken?", "For juicy chicken, marinate for 30 minutes, cook at medium heat, and rest for 5 minutes after cooking.", "Cooking", "chicken cooking method"),
        ("How do I make chocolate cake?", "Mix flour, sugar, eggs, butter, and chocolate. Bake at 350°F for 30-35 minutes. Cool completely before serving.", "Cooking", "chocolate cake recipe baking"),
        ("What are essential kitchen ingredients?", "Essential ingredients include salt, oil, spices (cumin, turmeric, chili), flour, sugar, garlic, and ginger.", "Cooking", "kitchen ingredients essential"),
        ("How do I make dal (lentils)?", "Boil lentils with water, add turmeric and salt. In a separate pan, sauté cumin and onions, then add to lentils.", "Cooking", "dal lentils recipe"),
        ("What's the best rice cooking method?", "Use 1:2 rice to water ratio. Bring to boil, then simmer on low heat for 18-20 minutes until water is absorbed.", "Cooking", "rice cooking method"),
        ("How do I make homemade pizza?", "Mix flour, water, salt, and yeast for dough. Let rise 1 hour. Add toppings and bake at 475°F for 12-15 minutes.", "Cooking", "pizza homemade recipe"),
        ("What's the best way to make samosas?", "Prepare potato filling with peas and spices, wrap in pastry triangles, and deep fry until golden. Serve hot with chutney.", "Cooking", "samosas recipe deep fry"),
        
        # Motor Vehicles Around the World (10)
        ("What are the fastest cars in the world?", "The fastest production cars include Bugatti Bolide (303+ mph), SSC Tuatara, and Koenigsegg Jesko Absolut.", "Motor Vehicles", "fastest cars speed world"),
        ("What's the difference between automatic and manual transmission?", "Manual requires driver to shift gears, while automatic shifts automatically. Manual offers more control, automatic offers convenience.", "Motor Vehicles", "transmission automatic manual"),
        ("How often should I service my car?", "Most cars need servicing every 10,000-15,000 km or every 6-12 months, whichever comes first.", "Motor Vehicles", "car service maintenance schedule"),
        ("What are electric vehicles?", "Electric vehicles (EVs) are powered by rechargeable batteries instead of gasoline. Examples: Tesla, BMW i8, Nissan Leaf.", "Motor Vehicles", "electric vehicles EV battery"),
        ("What's the best fuel efficiency?", "Hybrid cars like Toyota Prius achieve 50+ mpg. Electric vehicles can travel 200-300 miles per charge.", "Motor Vehicles", "fuel efficiency mpg hybrid"),
        ("How do I maintain my bike?", "Regularly check tire pressure, oil level, chain tension, and brake condition. Get professional servicing annually.", "Motor Vehicles", "bike motorcycle maintenance"),
        ("What are luxury car brands?", "Top luxury brands include Mercedes-Benz, BMW, Audi, Lexus, Porsche, Ferrari, and Rolls-Royce.", "Motor Vehicles", "luxury car brands expensive"),
        ("What's the cost of a new car?", "Budget cars: $10,000-20,000. Mid-range: $20,000-40,000. Luxury: $40,000-100,000+. Premium: $100,000+", "Motor Vehicles", "car cost price new"),
        ("How do I improve car safety?", "Maintain tires, check brakes, install airbags, use seat belts, avoid distractions, and drive defensively.", "Motor Vehicles", "car safety tips"),
        ("What's the most popular car brand globally?", "Toyota leads globally followed by Volkswagen, General Motors, Hyundai, and BMW in terms of sales volume.", "Motor Vehicles", "popular car brands global"),
        
        # Health & Wellness (10)
        ("What's a healthy daily routine?", "Wake early, exercise 30 minutes, eat balanced meals, stay hydrated, practice mindfulness, and sleep 7-8 hours.", "Health & Wellness", "daily routine healthy lifestyle"),
        ("How much water should I drink daily?", "Generally, aim for 8-10 glasses (2-3 liters) of water daily. Adjust based on activity level and climate.", "Health & Wellness", "water intake hydration daily"),
        ("What are the benefits of yoga?", "Yoga improves flexibility, reduces stress, strengthens core, improves breathing, and enhances mental clarity.", "Health & Wellness", "yoga benefits exercise"),
        ("How can I prevent common cold?", "Wash hands frequently, avoid touching face, get adequate sleep, eat vitamin C-rich foods, and stay vaccinated.", "Health & Wellness", "common cold prevention tips"),
        ("What's a balanced diet?", "Include proteins (chicken, fish, beans), carbs (whole grains), fats (olive oil), vegetables, and fruits in each meal.", "Health & Wellness", "balanced diet nutrition food"),
        ("How does exercise help mental health?", "Regular exercise reduces anxiety, improves mood through endorphins, helps manage stress, and boosts self-esteem.", "Health & Wellness", "exercise mental health stress"),
        ("What are superfoods?", "Superfoods include berries, kale, salmon, almonds, avocado, dark chocolate, and turmeric with high nutritional value.", "Health & Wellness", "superfoods nutrition health"),
        ("How can I sleep better?", "Maintain consistent sleep schedule, avoid screens before bed, keep room cool, practice relaxation, and avoid caffeine.", "Health & Wellness", "sleep better insomnia tips"),
        ("What's the right way to stretch?", "Hold stretches for 15-30 seconds, never bounce, focus on major muscle groups, and stretch after warm-up.", "Health & Wellness", "stretching exercise flexibility"),
        ("How often should I exercise?", "Aim for 150 minutes moderate aerobic activity or 75 minutes vigorous activity per week, plus strength training 2 days.", "Health & Wellness", "exercise frequency weekly guidelines"),
        
        # Technology Tips (10)
        ("How do I protect my laptop from viruses?", "Use reputable antivirus software, keep OS updated, don't open suspicious emails, avoid unreliable websites.", "Technology Tips", "laptop virus protection security"),
        ("What's the difference between RAM and storage?", "RAM is temporary memory for active tasks (faster, resets on restart). Storage is permanent memory (slower, retains data).", "Technology Tips", "RAM storage memory difference"),
        ("How can I speed up my computer?", "Delete unnecessary files, disable startup programs, update drivers, run antivirus scans, and upgrade RAM if needed.", "Technology Tips", "computer speed optimization"),
        ("What are cloud services?", "Cloud services store data on remote servers accessible via internet. Examples: Google Drive, Dropbox, OneDrive.", "Technology Tips", "cloud storage services"),
        ("How do I create a strong password?", "Use 12+ characters with uppercase, lowercase, numbers, and symbols. Avoid personal info and common words.", "Technology Tips", "strong password security"),
        ("What's the difference between WiFi and Bluetooth?", "WiFi connects to internet wirelessly over longer range. Bluetooth connects devices directly over shorter range.", "Technology Tips", "WiFi Bluetooth wireless difference"),
        ("How do I backup my phone data?", "Use cloud backup (Google/iCloud), computer sync, or external storage. Backup automatically weekly.", "Technology Tips", "backup phone data safety"),
        ("What are cookies on websites?", "Cookies are small files websites store on your browser to remember preferences, login info, and browsing history.", "Technology Tips", "cookies website tracking"),
        ("How do I fix a frozen computer?", "Try force quit (Alt+F4), Task Manager (Ctrl+Shift+Esc), restart, or safe mode. Last resort: hard reset.", "Technology Tips", "frozen computer fix restart"),
        ("What's artificial intelligence?", "AI is computer systems designed to mimic human intelligence for tasks like learning, problem-solving, and pattern recognition.", "Technology Tips", "artificial intelligence AI machine learning"),
        
        # Travel Tips (10)
        ("What should I pack for a trip?", "Pack clothes for climate, comfortable shoes, toiletries, medications, documents, phone charger, and minimal accessories.", "Travel Tips", "packing list trip travel"),
        ("How can I find cheap flights?", "Book 6 weeks in advance, compare sites (Skyscanner, Kayak), be flexible with dates, use flight alerts, and travel mid-week.", "Travel Tips", "cheap flights booking deals"),
        ("What documents do I need to travel?", "Passport (valid 6+ months), visa if required, travel insurance, vaccination records, and copies of important documents.", "Travel Tips", "travel documents passport visa"),
        ("How do I overcome jet lag?", "Adjust sleep schedule before travel, stay hydrated, get sunlight, avoid caffeine, and adapt to local time immediately.", "Travel Tips", "jet lag prevention cure"),
        ("What are travel insurance benefits?", "Travel insurance covers medical emergencies, trip cancellations, lost luggage, flight delays, and evacuation costs.", "Travel Tips", "travel insurance benefits coverage"),
        ("How should I exchange currency?", "Exchange at banks or ATMs for best rates. Avoid airport exchanges. Notify bank of travel to avoid card blocks.", "Travel Tips", "currency exchange travel rates"),
        ("What are must-see destinations?", "Popular destinations: Paris, Tokyo, New York, Dubai, Rome, Barcelona, Singapore, and Bali.", "Travel Tips", "travel destinations must-see"),
        ("How can I travel on a budget?", "Use public transport, stay in hostels, eat at local restaurants, book packages, and travel in off-season.", "Travel Tips", "budget travel cheap accommodation"),
        ("What's the best travel season?", "Generally spring (March-May) and fall (September-November) offer pleasant weather and fewer crowds.", "Travel Tips", "best travel season weather"),
        ("How do I stay safe while traveling?", "Keep valuables secure, use hotel safe, stay aware of surroundings, avoid empty streets at night, and share itinerary.", "Travel Tips", "travel safety tips secure"),
        
        # Business & Career (10)
        ("How do I write an effective resume?", "Include contact info, summary, work experience, education, skills. Keep it 1 page, use clear formatting, and tailor to job.", "Business & Career", "resume writing job application"),
        ("What makes a good job interview?", "Research company, arrive early, dress professionally, answer confidently, ask questions, and follow up with thank you email.", "Business & Career", "job interview tips preparation"),
        ("How can I negotiate salary?", "Research market rates, highlight achievements, ask confidently, be willing to walk away, and negotiate all benefits.", "Business & Career", "salary negotiation career"),
        ("What are soft skills employers want?", "Communication, teamwork, leadership, problem-solving, time management, creativity, and adaptability are highly valued.", "Business & Career", "soft skills employment"),
        ("How do I start a business?", "Identify market need, create business plan, secure funding, register business, build team, and execute launch strategy.", "Business & Career", "start business entrepreneurship"),
        ("What's the difference between startup and established business?", "Startups are new ventures with high growth potential but risk. Established businesses are stable with proven models.", "Business & Career", "startup business difference"),
        ("How should I invest for retirement?", "Start early, use 401k/IRA, invest in stocks and bonds, diversify portfolio, and consult financial advisor.", "Business & Career", "retirement investment planning"),
        ("What are professional certifications worth?", "Certifications increase earning potential 15-25%, improve job prospects, demonstrate expertise, and provide career advancement.", "Business & Career", "professional certification value"),
        ("How do I build professional network?", "Attend industry events, join associations, connect on LinkedIn, help others, and maintain relationships regularly.", "Business & Career", "networking professional relationships"),
        ("What's important for career growth?", "Continuous learning, skill development, seeking mentorship, taking on challenges, and building strong professional relationships.", "Business & Career", "career growth advancement tips"),
        
        # Fashion & Style (10)
        ("What's the best style for my body type?", "Pear shape: darker bottoms, lighter tops. Apple: A-line dresses. Rectangle: fitted clothing. Hourglass: fitted styles.", "Fashion & Style", "body type style fashion"),
        ("How do I build a capsule wardrobe?", "Start with neutral basics (5 shirts, 3 pants), add versatile layers, choose 1-2 accent colors, and select quality pieces.", "Fashion & Style", "capsule wardrobe basics"),
        ("What colors look good together?", "Complementary pairs: blue-orange, red-green, yellow-purple. Monochromatic uses shades of one color.", "Fashion & Style", "color combinations fashion"),
        ("How should I dress for a job interview?", "Business formal: suit and tie. Business casual: dress pants/skirt with blouse. Conservative colors, polished shoes.", "Fashion & Style", "job interview dress code"),
        ("What are current fashion trends?", "Popular trends include oversized fits, sustainable fashion, vintage pieces, earth tones, and statement accessories.", "Fashion & Style", "fashion trends current"),
        ("How do I accessorize an outfit?", "Choose 2-3 accessories max. Balance proportions: delicate with simple, bold with minimalist. Match metal tones.", "Fashion & Style", "accessorize outfit jewelry"),
        ("What's smart casual?", "Smart casual includes dark jeans, casual shirts with blazer, loafers, neat appearance. Avoid athletic wear and sloppy fits.", "Fashion & Style", "smart casual dress code"),
        ("How do I care for expensive clothes?", "Follow care labels, wash delicates by hand, hang dry, store properly, and use mothballs for wool.", "Fashion & Style", "clothing care maintenance"),
        ("What shoes go with everything?", "White sneakers, neutral flats, classic pumps, and loafers are versatile and work with most outfits.", "Fashion & Style", "versatile shoes wardrobe"),
        ("How do I find my personal style?", "Collect inspiration, identify recurring patterns, know your lifestyle needs, invest in quality basics, and express personality.", "Fashion & Style", "personal style fashion identity"),
        
        # Sports (10)
        ("What are the health benefits of sports?", "Sports improve cardiovascular health, build muscle, reduce stress, enhance mental focus, and promote social connections.", "Sports", "sports health benefits fitness"),
        ("What's the difference between sports and exercise?", "Exercise is physical activity for fitness. Sports involve competition, rules, and often teams with specific goals.", "Sports", "sports exercise difference"),
        ("How should I warm up before sports?", "5-10 minute light cardio, dynamic stretches for 5 minutes, sport-specific movements, and gradual intensity increase.", "Sports", "warm up before exercise sports"),
        ("What are major sports worldwide?", "Soccer/Football, Cricket, Basketball, Tennis, Hockey, Volleyball, American Football, Baseball, and Rugby.", "Sports", "major sports worldwide"),
        ("How do I improve athletic performance?", "Train regularly, maintain proper nutrition, get adequate sleep, stay hydrated, use correct technique, and cross-train.", "Sports", "athletic performance improvement training"),
        ("What's the purpose of cool-down?", "Cool-down brings heart rate down, prevents dizziness, aids recovery, reduces muscle soreness, and prepares body for rest.", "Sports", "cool down exercise recovery"),
        ("What are Olympic games?", "International sporting event held every 4 years showcasing 300+ events across 28 sports with athletes from 200+ countries.", "Sports", "Olympics games events sports"),
        ("How do I prevent sports injuries?", "Warm up properly, use correct technique, wear protective gear, don't overtraining, and gradually increase intensity.", "Sports", "injury prevention sports safety"),
        ("What's cross-training?", "Training in multiple sports or activities to improve overall fitness, prevent injury, and maintain motivation.", "Sports", "cross training fitness"),
        ("What are common sports injuries?", "Common injuries include sprains, strains, muscle pulls, stress fractures, and tendonitis. Seek medical help for severe pain.", "Sports", "sports injuries common treatment"),
        
        # Environment & Sustainability (10)
        ("What's climate change?", "Climate change is long-term shift in global temperatures and weather patterns, primarily caused by human activities increasing greenhouse gases.", "Environment & Sustainability", "climate change global warming"),
        ("How can I reduce my carbon footprint?", "Use public transport, reduce energy use, eat less meat, recycle, buy local products, and use renewable energy.", "Environment & Sustainability", "carbon footprint reduction"),
        ("What are renewable energy sources?", "Solar, wind, hydroelectric, geothermal, and biomass are renewable sources that naturally replenish and don't deplete.", "Environment & Sustainability", "renewable energy sources"),
        ("Why is recycling important?", "Recycling reduces waste in landfills, conserves resources, saves energy, reduces pollution, and decreases manufacturing needs.", "Environment & Sustainability", "recycling importance environmental"),
        ("What's sustainable development?", "Development that meets current needs without compromising future generations' ability to meet their needs.", "Environment & Sustainability", "sustainable development environment"),
        ("How do I practice eco-friendly living?", "Use reusable bags, reduce plastic, conserve water, compost, use eco-friendly products, and support sustainable brands.", "Environment & Sustainability", "eco-friendly living sustainable"),
        ("What's deforestation impact?", "Deforestation causes habitat loss, increases carbon levels, affects water cycles, reduces biodiversity, and causes climate disruption.", "Environment & Sustainability", "deforestation environmental impact"),
        ("How can businesses be sustainable?", "Use renewable energy, reduce waste, ethical sourcing, minimize packaging, support circular economy, and carbon offset.", "Environment & Sustainability", "sustainable business practices"),
        ("What's a carbon footprint?", "Total greenhouse gases produced by human activities. Average person produces 4-5 tons annually; target is under 3 tons.", "Environment & Sustainability", "carbon footprint measurement"),
        ("Why protect endangered species?", "Protect biodiversity, maintain ecosystem balance, preserve natural heritage, ensure food security, and maintain climate stability.", "Environment & Sustainability", "endangered species protection"),
        
        # Personal Finance (10)
        ("How do I create a budget?", "Track income, list expenses, categorize spending, set limits per category, and review monthly to stay on track.", "Personal Finance", "budget creation personal finance"),
        ("What's the difference between saving and investing?", "Saving keeps money safe with low returns. Investing puts money in assets for higher growth potential but with risk.", "Personal Finance", "saving investing difference"),
        ("How should I manage debt?", "Make minimum payments, prioritize high-interest debt, consider consolidation, create payment plan, and seek professional help if needed.", "Personal Finance", "debt management personal finance"),
        ("What are different investment types?", "Stocks, bonds, mutual funds, ETFs, real estate, and savings accounts offer different risk-return profiles.", "Personal Finance", "investment types options"),
        ("How do I build an emergency fund?", "Save 3-6 months expenses in liquid account. Start with $1000, automate transfers, and don't touch unless emergency.", "Personal Finance", "emergency fund savings"),
        ("What's compound interest?", "Interest earned on both principal and previous interest. Long-term investing maximizes compound growth exponentially.", "Personal Finance", "compound interest investing"),
        ("How do I improve credit score?", "Pay bills on time, reduce debt, keep credit utilization under 30%, don't close old accounts, and dispute errors.", "Personal Finance", "credit score improvement"),
        ("What's inflation impact?", "Inflation reduces money's purchasing power. $100 today may be worth $90 next year. Invest to outpace inflation.", "Personal Finance", "inflation impact money"),
        ("Should I buy or rent?", "Buying: long-term investment, stability, equity. Renting: flexibility, lower commitment, maintenance included. Depends on goals.", "Personal Finance", "buy vs rent housing"),
        ("How do I plan for retirement?", "Start early, max out 401k/IRA, diversify investments, monitor progress, and adjust as you age and goals change.", "Personal Finance", "retirement planning investment"),
        
        # Entertainment (10)
        ("What are the best movies of all time?", "Classic must-watch films: Shawshank Redemption, Godfather, Pulp Fiction, Inception, Titanic, Avatar, and Lord of the Rings.", "Entertainment", "best movies films watch"),
        ("What are popular streaming services?", "Netflix, Amazon Prime, Disney+, HBO Max, Hulu, Apple TV+, and Paramount+ offer various entertainment content.", "Entertainment", "streaming services movies shows"),
        ("What's the difference between movies and series?", "Movies are self-contained 2-3 hours. Series span multiple seasons with ongoing storylines and character development.", "Entertainment", "movies series difference TV"),
        ("What are popular music genres?", "Pop, rock, hip-hop, R&B, country, jazz, classical, electronic, indie, and folk are major genres globally.", "Entertainment", "music genres popular styles"),
        ("How do I discover new music?", "Use Spotify recommendations, follow artists, join music communities, listen to radio, watch music videos, and ask friends.", "Entertainment", "discover new music playlists"),
        ("What are world's best music festivals?", "Coachella, Glastonbury, Lollapalooza, Burning Man, Tomorrowland, and Comic-Con are iconic entertainment events.", "Entertainment", "music festivals world famous"),
        ("What makes a good video game?", "Engaging gameplay, compelling story, good graphics, responsive controls, replayability, and community features.", "Entertainment", "good video game elements"),
        ("What are popular video game genres?", "Action, RPG, Strategy, FPS, Adventure, Sports, Racing, Puzzle, and Simulation are major gaming genres.", "Entertainment", "video game genres popular"),
        ("How do I start gaming?", "Choose platform (PC, Console, Mobile), select games matching interests, start with popular titles, and join communities.", "Entertainment", "gaming start beginner"),
        ("What's virtual reality entertainment?", "VR creates immersive 3D environments using headsets. Applications include games, movies, training, and experiences.", "Entertainment", "virtual reality VR entertainment"),
    ]
    
    for question, answer, category, keywords in sample_faqs:
        try:
            cursor.execute(
                'INSERT INTO faqs (question, answer, category, keywords) VALUES (?, ?, ?, ?)',
                (question, answer, category, keywords)
            )
        except sqlite3.IntegrityError:
            pass  # Skip duplicates
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_database()
    insert_sample_faqs()
    print("Database initialized successfully!")
