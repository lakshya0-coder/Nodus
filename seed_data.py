"""
Seed script — Populates the database with demo data for Nodus Cafe.
Run: python seed_data.py
"""
import os
import sys
import random
from datetime import datetime, timedelta, date

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db
from app.models.user import User
from app.models.menu import MenuCategory, MenuItem
from app.models.booking import Booking
from app.models.order import Order, OrderItem
from app.models.setting import Setting


def seed():
    app = create_app()

    with app.app_context():
        print("🌱 Seeding Nodus Cafe database...")

        # --- Users ---
        print("  → Creating users...")
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@noduscafe.com',
                full_name='Cafe Owner',
                role='developer',
                preferred_language='en'
            )
            admin.set_password('admin123')
            db.session.add(admin)

        if not User.query.filter_by(username='staff1').first():
            staff = User(
                username='staff1',
                email='staff@noduscafe.com',
                full_name='Barista Raj',
                role='staff',
                preferred_language='hi'
            )
            staff.set_password('staff123')
            db.session.add(staff)

        db.session.commit()

        # --- Menu Categories ---
        print("  → Creating menu categories...")
        categories_data = [
            {'name_en': 'Coffee', 'name_hi': 'कॉफ़ी', 'icon': '', 'order': 1},
            {'name_en': 'Tea', 'name_hi': 'चाय', 'icon': '', 'order': 2},
            {'name_en': 'Cold Beverages', 'name_hi': 'ठंडे पेय', 'icon': '', 'order': 3},
            {'name_en': 'Smoothies & Shakes', 'name_hi': 'स्मूदी और शेक', 'icon': '', 'order': 4},
            {'name_en': 'Snacks', 'name_hi': 'स्नैक्स', 'icon': '', 'order': 5},
            {'name_en': 'Desserts', 'name_hi': 'मिठाई', 'icon': '', 'order': 6},
        ]

        categories = {}
        for cat_data in categories_data:
            existing = MenuCategory.query.filter_by(name_en=cat_data['name_en']).first()
            if not existing:
                cat = MenuCategory(
                    name_en=cat_data['name_en'],
                    name_hi=cat_data['name_hi'],
                    icon=cat_data['icon'],
                    display_order=cat_data['order'],
                    is_active=True
                )
                db.session.add(cat)
                db.session.flush()
                categories[cat_data['name_en']] = cat.id
            else:
                categories[cat_data['name_en']] = existing.id

        db.session.commit()

        # --- Menu Items ---
        print("  → Creating menu items...")
        items_data = [
            # Coffee
            {'cat': 'Coffee', 'name_en': 'Artisan Latte', 'name_hi': 'आर्टिज़न लैटे',
             'desc_en': 'Our signature espresso perfectly balanced with silky, textured steamed milk and poured with intricate rosetta art.',
             'desc_hi': 'हमारा सिग्नेचर एस्प्रेसो रेशमी, स्टीम्ड दूध के साथ पूरी तरह संतुलित और जटिल रोज़ेटा आर्ट के साथ परोसा गया।',
             'price': 249, 'tags': ['Bestseller'], 'image_path': 'images/drink_latte.png'},
            {'cat': 'Coffee', 'name_en': 'Double Shot Espresso', 'name_hi': 'डबल शॉट एस्प्रेसो',
             'desc_en': 'Two bold espresso shots extracted to perfection with a thick, golden crema. Pure and intense.',
             'desc_hi': 'दो बोल्ड एस्प्रेसो शॉट सुनहरे क्रेमा के साथ पूर्णता तक निकाले गए। शुद्ध और तीव्र।',
             'price': 179, 'tags': [], 'image_path': 'images/drink_espresso.png'},
            {'cat': 'Coffee', 'name_en': 'Cappuccino', 'name_hi': 'कैपुचिनो',
             'desc_en': 'Velvety steamed milk with a double espresso shot, topped with silky foam art.',
             'desc_hi': 'मखमली स्टीम्ड दूध डबल एस्प्रेसो शॉट के साथ, रेशमी फोम आर्ट से सजा हुआ।',
             'price': 199, 'tags': ['Bestseller', 'Popular'], 'image_path': ''},
            {'cat': 'Coffee', 'name_en': 'Caramel Latte', 'name_hi': 'कैरामेल लैटे',
             'desc_en': 'Smooth latte infused with house-made caramel syrup and a drizzle on top.',
             'desc_hi': 'घर में बना कैरामेल सिरप मिलाकर तैयार स्मूथ लैटे, ऊपर से कैरामेल की बूँदें।',
             'price': 249, 'tags': ['Popular'], 'image_path': ''},
            {'cat': 'Coffee', 'name_en': 'Mocha', 'name_hi': 'मोका',
             'desc_en': 'Rich espresso meets premium dark chocolate and steamed milk. A chocolate lover\'s dream.',
             'desc_hi': 'रिच एस्प्रेसो, प्रीमियम डार्क चॉकलेट और स्टीम्ड दूध। चॉकलेट प्रेमियों का सपना।',
             'price': 269, 'tags': []},
            {'cat': 'Coffee', 'name_en': 'Lavender Latte', 'name_hi': 'लैवेंडर लैटे',
             'desc_en': 'Aromatic lavender-infused latte with oat milk. Calming and unique.',
             'desc_hi': 'खुशबूदार लैवेंडर लैटे ओट मिल्क के साथ। शांत और अनोखा।',
             'price': 289, 'tags': ['New', 'Vegan']},
            {'cat': 'Coffee', 'name_en': 'Double Shot Americano', 'name_hi': 'डबल शॉट अमेरिकानो',
             'desc_en': 'Two bold espresso shots diluted with hot water. Strong and smooth.',
             'desc_hi': 'दो बोल्ड एस्प्रेसो शॉट गर्म पानी के साथ। स्ट्रॉन्ग और स्मूथ।',
             'price': 179, 'tags': []},
            {'cat': 'Coffee', 'name_en': 'Hazelnut Mocha', 'name_hi': 'हेज़लनट मोका',
             'desc_en': 'Decadent hazelnut and chocolate combined with a strong espresso base.',
             'desc_hi': 'शानदार हेज़लनट और चॉकलेट, स्ट्रॉन्ग एस्प्रेसो बेस के साथ।',
             'price': 279, 'tags': ['New']},

            # Tea
            {'cat': 'Tea', 'name_en': 'Masala Chai', 'name_hi': 'मसाला चाय',
             'desc_en': 'Traditional Indian spiced tea with fresh ginger, cardamom, and whole milk.',
             'desc_hi': 'पारंपरिक भारतीय मसाला चाय ताज़ी अदरक, इलायची और दूध के साथ।',
             'price': 99, 'tags': ['Bestseller']},
            {'cat': 'Tea', 'name_en': 'Green Tea', 'name_hi': 'ग्रीन टी',
             'desc_en': 'Premium Japanese green tea, delicately brewed. Light and refreshing.',
             'desc_hi': 'प्रीमियम जापानी ग्रीन टी, हल्की और ताज़गी भरी।',
             'price': 129, 'tags': ['Vegan']},
            {'cat': 'Tea', 'name_en': 'Earl Grey', 'name_hi': 'अर्ल ग्रे',
             'desc_en': 'Classic bergamot-flavored black tea with a touch of honey.',
             'desc_hi': 'क्लासिक बर्गमोट फ्लेवर्ड ब्लैक टी, शहद की एक बूँद के साथ।',
             'price': 149, 'tags': []},
            {'cat': 'Tea', 'name_en': 'Chamomile Dream', 'name_hi': 'कैमोमाइल ड्रीम',
             'desc_en': 'Soothing chamomile herbal tea with a hint of vanilla. Perfect for unwinding.',
             'desc_hi': 'शांत कैमोमाइल हर्बल टी, वनीला की हल्की छुअन के साथ।',
             'price': 159, 'tags': ['Vegan']},

            # Cold Beverages
            {'cat': 'Cold Beverages', 'name_en': 'Iced Caramel Macchiato', 'name_hi': 'आइस्ड कारमेल मैकियाटो',
             'desc_en': 'Premium iced macchiato featuring cascading espresso layered over chilled milk, finished with our house-made caramel drizzle.',
             'desc_hi': 'प्रीमियम आइस्ड मैकियाटो ठंडे दूध के ऊपर कैस्केडिंग एस्प्रेसो के साथ, और हमारे घर के बने कारमेल ड्रिज़ल के साथ समाप्त होता है।',
             'price': 289, 'tags': ['Popular'], 'image_path': 'images/drink_macchiato.png'},
            {'cat': 'Cold Beverages', 'name_en': 'Cold Brew', 'name_hi': 'कोल्ड ब्रू',
             'desc_en': '18-hour slow-steeped cold brew. Smooth, low-acid, incredibly refreshing.',
             'desc_hi': '18 घंटे धीमी भिगोई हुई कोल्ड ब्रू। स्मूथ, कम एसिड, अविश्वसनीय रूप से ताज़ा।',
             'price': 229, 'tags': ['Bestseller'], 'image_path': ''},
            {'cat': 'Cold Beverages', 'name_en': 'Iced Matcha Latte', 'name_hi': 'आइस्ड माचा लैटे',
             'desc_en': 'Ceremonial-grade vibrant green matcha whisked with chilled oat milk and served over ice.',
             'desc_hi': 'सेरेमोनियल-ग्रेड वाइब्रेंट ग्रीन माचा ठंडे ओट मिल्क और बर्फ़ के साथ।',
             'price': 259, 'tags': ['Vegan', 'New'], 'image_path': 'images/drink_matcha.png'},
            {'cat': 'Cold Beverages', 'name_en': 'Rose Lemonade', 'name_hi': 'रोज़ लेमोनेड',
             'desc_en': 'Fresh lemonade with a splash of rose syrup and mint leaves.',
             'desc_hi': 'ताज़ा नींबू पानी गुलाब के शर्बत और पुदीने की पत्तियों के साथ।',
             'price': 169, 'tags': ['Vegan']},

            # Smoothies & Shakes
            {'cat': 'Smoothies & Shakes', 'name_en': 'Mango Tango Smoothie', 'name_hi': 'मैंगो टैंगो स्मूदी',
             'desc_en': 'Ripe Alphonso mango blended with yogurt and a hint of cardamom.',
             'desc_hi': 'पका अल्फोंसो आम दही और इलायची की हल्की खुशबू के साथ।',
             'price': 219, 'tags': ['Popular']},
            {'cat': 'Smoothies & Shakes', 'name_en': 'Berry Bliss', 'name_hi': 'बेरी ब्लिस',
             'desc_en': 'Mixed berries with banana and almond milk. Antioxidant-rich delight.',
             'desc_hi': 'मिक्स्ड बेरीज़, केला और बादाम दूध। एंटीऑक्सीडेंट से भरपूर।',
             'price': 239, 'tags': ['Vegan']},
            {'cat': 'Smoothies & Shakes', 'name_en': 'Chocolate Peanut Butter Shake', 'name_hi': 'चॉकलेट पीनट बटर शेक',
             'desc_en': 'Indulgent dark chocolate and peanut butter milkshake. Pure comfort.',
             'desc_hi': 'डार्क चॉकलेट और पीनट बटर मिल्कशेक। पूर्ण आनंद।',
             'price': 269, 'tags': ['Popular']},

            # Snacks
            {'cat': 'Snacks', 'name_en': 'Avocado Toast', 'name_hi': 'एवोकाडो टोस्ट',
             'desc_en': 'Sourdough toast topped with smashed avocado, cherry tomatoes, and microgreens.',
             'desc_hi': 'सॉरडो टोस्ट पर एवोकाडो, चेरी टमाटर और माइक्रोग्रीन्स।',
             'price': 299, 'tags': ['Vegan', 'Popular']},
            {'cat': 'Snacks', 'name_en': 'Paneer Tikka Wrap', 'name_hi': 'पनीर टिक्का रैप',
             'desc_en': 'Grilled paneer tikka in a whole wheat wrap with mint chutney and onions.',
             'desc_hi': 'ग्रिल्ड पनीर टिक्का, गेहूँ के रैप में पुदीने की चटनी और प्याज़ के साथ।',
             'price': 249, 'tags': ['Spicy', 'Bestseller']},
            {'cat': 'Snacks', 'name_en': 'Croissant (Butter)', 'name_hi': 'क्रोसॉन्ट (बटर)',
             'desc_en': 'Flaky, golden butter croissant baked fresh every morning.',
             'desc_hi': 'परतदार, सुनहरा बटर क्रोसॉन्ट, हर सुबह ताज़ा बेक किया हुआ।',
             'price': 149, 'tags': []},
            {'cat': 'Snacks', 'name_en': 'Loaded Nachos', 'name_hi': 'लोडेड नाचोज़',
             'desc_en': 'Crispy nachos with melted cheese, jalapeños, salsa, and sour cream.',
             'desc_hi': 'क्रिस्पी नाचोज़ पिघले चीज़, हलपेनो, सालसा और सॉर क्रीम के साथ।',
             'price': 279, 'tags': ['Spicy']},

            # Desserts
            {'cat': 'Desserts', 'name_en': 'Tiramisu', 'name_hi': 'तिरामिसू',
             'desc_en': 'Classic Italian dessert with layers of espresso-soaked ladyfingers and mascarpone.',
             'desc_hi': 'क्लासिक इटालियन डेज़र्ट, एस्प्रेसो में भिगोई लेडीफिंगर्स और मस्कारपोन।',
             'price': 349, 'tags': ['Bestseller']},
            {'cat': 'Desserts', 'name_en': 'New York Cheesecake', 'name_hi': 'न्यूयॉर्क चीज़केक',
             'desc_en': 'Creamy, dense cheesecake with a graham cracker crust and berry compote.',
             'desc_hi': 'क्रीमी, घना चीज़केक ग्राहम क्रैकर क्रस्ट और बेरी कम्पोट के साथ।',
             'price': 329, 'tags': ['Popular']},
            {'cat': 'Desserts', 'name_en': 'Chocolate Lava Cake', 'name_hi': 'चॉकलेट लावा केक',
             'desc_en': 'Warm, gooey chocolate cake with a molten center. Served with vanilla ice cream.',
             'desc_hi': 'गर्म, गूई चॉकलेट केक पिघले सेंटर के साथ। वनीला आइसक्रीम के साथ परोसा जाता है।',
             'price': 299, 'tags': ['New']},
            {'cat': 'Desserts', 'name_en': 'Gulab Jamun', 'name_hi': 'गुलाब जामुन',
             'desc_en': 'Soft, golden dumplings soaked in rose-scented sugar syrup. A Nodus twist on a classic.',
             'desc_hi': 'नर्म, सुनहरे गुलाब जामुन गुलाब की खुशबू वाली चाशनी में। नोडस का क्लासिक ट्विस्ट।',
             'price': 199, 'tags': ['Popular']},
        ]

        for item_data in items_data:
            existing = MenuItem.query.filter_by(name_en=item_data['name_en']).first()
            if not existing:
                item = MenuItem(
                    category_id=categories[item_data['cat']],
                    name_en=item_data['name_en'],
                    name_hi=item_data['name_hi'],
                    description_en=item_data['desc_en'],
                    description_hi=item_data['desc_hi'],
                    price=item_data['price'],
                    image_path=item_data.get('image_path', ''),
                    is_available=True,
                    display_order=items_data.index(item_data)
                )
                item.set_tags(item_data['tags'])
                db.session.add(item)

        db.session.commit()

        # --- Sample Bookings (for ML training) ---
        print("  → Creating sample bookings for ML training...")
        customer_names = [
            'Aarav Sharma', 'Diya Patel', 'Vivaan Gupta', 'Ananya Singh',
            'Arjun Reddy', 'Meera Iyer', 'Kabir Khan', 'Riya Joshi',
            'Aditya Nair', 'Pooja Verma', 'Rohit Malhotra', 'Sneha Das',
            'Karthik Rao', 'Ishita Bhat', 'Nikhil Shetty'
        ]

        time_slots = [f"{h:02d}:00-{h+1:02d}:00" for h in range(8, 22)]

        # Generate bookings for the past 4 weeks
        today = date.today()
        for day_offset in range(28, 0, -1):
            booking_date = today - timedelta(days=day_offset)
            weekday = booking_date.weekday()
            is_weekend = weekday >= 5

            # More bookings on weekends and during peak hours
            num_bookings = random.randint(3, 8) if is_weekend else random.randint(2, 6)

            for _ in range(num_bookings):
                # Weighted time slot selection (busier at lunch/evening)
                weights = []
                for h in range(8, 22):
                    if 12 <= h <= 14:
                        weights.append(4)
                    elif 17 <= h <= 20:
                        weights.append(3)
                    elif 9 <= h <= 11:
                        weights.append(2)
                    else:
                        weights.append(1)

                slot = random.choices(time_slots, weights=weights, k=1)[0]
                guests = random.choices([1, 2, 3, 4, 5, 6], weights=[15, 30, 20, 15, 10, 10], k=1)[0]

                status = random.choices(
                    ['completed', 'confirmed', 'cancelled', 'no_show'],
                    weights=[60, 20, 10, 10], k=1
                )[0]

                # Only past bookings should be completed
                if booking_date >= today:
                    status = 'confirmed'

                booking = Booking(
                    booking_ref=Booking.generate_ref(booking_date),
                    customer_name=random.choice(customer_names),
                    customer_email=f"{random.choice(['user', 'guest', 'customer'])}{random.randint(1,99)}@email.com",
                    customer_phone=f"+91 {random.randint(70000,99999)} {random.randint(10000,99999)}",
                    date=booking_date,
                    time_slot=slot,
                    guest_count=guests,
                    seating_preference=random.choice(['indoor', 'outdoor', 'any']),
                    status=status
                )
                db.session.add(booking)

        db.session.commit()

        # --- Sample Orders ---
        print("  → Creating sample orders...")
        all_items = MenuItem.query.all()
        for i in range(15):
            order = Order(
                order_ref=Order.generate_ref(),
                customer_name=random.choice(customer_names),
                status=random.choice(['received', 'preparing', 'ready', 'completed']),
                notes=''
            )
            db.session.add(order)
            db.session.flush()

            # Add 1-4 items to each order
            for _ in range(random.randint(1, 4)):
                menu_item = random.choice(all_items)
                qty = random.randint(1, 3)
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=menu_item.id,
                    quantity=qty,
                    unit_price=menu_item.price
                )
                db.session.add(order_item)

            order.calculate_total()

        db.session.commit()

        # --- Generate initial predictions ---
        print("  → Generating initial demand predictions...")
        from app.services.ml_predictor import demand_predictor
        demand_predictor.init_app(app)
        result = demand_predictor.train()
        print(f"    ML Result: {result.get('message', result.get('error', 'Done'))}")

        print("\n✅ Seed complete!")
        print("=" * 50)
        print("  Admin Login:")
        print("    Username: admin")
        print("    Password: admin123")
        print("  Staff Login:")
        print("    Username: staff1")
        print("    Password: staff123")
        print("=" * 50)
        print(f"  Menu Items: {MenuItem.query.count()}")
        print(f"  Categories: {MenuCategory.query.count()}")
        print(f"  Bookings: {Booking.query.count()}")
        print(f"  Orders: {Order.query.count()}")
        print("=" * 50)


if __name__ == '__main__':
    seed()
