def get_website_name(url):
    website_options = {
        "Baby and Me": "https://www.bebe.nestle.ma/user/login?admin=123",
        "Kitkat": "https://kitkat2.factory.kitkat.com/user/login",
        "Maggi": "https://live-71956-food-maggi-me.pantheonsite.io/en/user/login",
        "Mom and Me Medical": "https://momandmemedical.nestle-mena.com/user/login?admin=123",
        "My Cancer My Nutrition": "https://live-dig0056055-nestlehealthscience-mcmn-mena.pantheonsite.io/en/user/126?check_logged_in=1",
        "My Child Nutrition": "http://big.nhscbrand.acsitefactory.com/user/login",
        "My Child With CP": "http://mychildwithcpmena.nhscbrand.acsitefactory.com/user/login",
        "Nature's Bounty": "https://live-dig0057429-natures-bounty-uae-united-arab-emirate.pantheonsite.io/user/login",
        "Nconnect": "https://live-dig0076096-nhsc-nhsc-mena.pantheonsite.io/user/login",
        "Nestlé Family": "https://www.nestle-family.com/en/admin-login",
        "Nestlé Family Nes": "https://www.nestlefamilynes-mena.com/user/login?admin=123",
        "Nestlé Mena": "https://me.factory.nestle.com/en/user/login",
        "Nestlé for Healthier Kids": "https://live-73063--nestleforhealthierkids-unitedarabemirates.pantheonsite.io/user/login",
        "Nestlé Goodnes": "https://test-dig0077344-multicategory-multibrand-france.pantheonsite.io/user/login",
        "Nestlé Health Science": "https://live-61547-healthscience-corporate-me.pantheonsite.io/user/login",
        "Nestlé Professional": "https://www.nestleprofessionalmena.com/ae/en/HrpeJQiz4ta4o9PSB2YkHhR4/login",
        "NIDO": "https://www.nidolove.com/admin-login",
        "Purina": "https://live-dig0030543-petcare-purinattt-arabia.pantheonsite.io/user/login",
        "Starbucks": "https://live-dig0048100-nestleprofessional-starbucks-uae.pantheonsite.io/en/user/login",
        "Vital protiens": "https://live-dig0054909-nhs-vitalproteins-mena.pantheonsite.io/en/user/login",
        "Wyeth Nutrition Parenting Community": "https://parentingcommunity.wyethnutrition.com/user/login?admin=123"
    }

    
    normalized_input = url.lower().replace('https://', '').replace('http://', '').rstrip('/')
    
    for name, site_url in website_options.items():
        normalized_site_url = site_url.lower().replace('https://', '').replace('http://', '').rstrip('/')
        
        if normalized_input in normalized_site_url or normalized_site_url in normalized_input:
            return name
    
    return None  

website_options = {
    "Baby and Me": "https://www.bebe.nestle.ma/user/login?admin=123",
    "Kitkat": "https://kitkat2.factory.kitkat.com/user/login",
    "Maggi": "https://live-71956-food-maggi-me.pantheonsite.io/en/user/login",
    "Mom and Me Medical": "https://momandmemedical.nestle-mena.com/user/login?admin=123",
    "My Cancer My Nutrition": "https://live-dig0056055-nestlehealthscience-mcmn-mena.pantheonsite.io/en/user/126?check_logged_in=1",
    "My Child Nutrition": "http://big.nhscbrand.acsitefactory.com/user/login",
    "My Child With CP": "http://mychildwithcpmena.nhscbrand.acsitefactory.com/user/login",
    "Nature's Bounty": "https://live-dig0057429-natures-bounty-uae-united-arab-emirate.pantheonsite.io/user/login",
    "Nconnect": "https://live-dig0076096-nhsc-nhsc-mena.pantheonsite.io/user/login",
    "Nestlé Family": "https://www.nestle-family.com/en/admin-login",
    "Nestlé Family Nes": "https://www.nestlefamilynes-mena.com/user/login?admin=123",
    "Nestlé Mena": "https://me.factory.nestle.com/en/user/login",
    "Nestlé for Healthier Kids": "https://live-73063--nestleforhealthierkids-unitedarabemirates.pantheonsite.io/user/login",
    "Nestlé Goodnes": "https://test-dig0077344-multicategory-multibrand-france.pantheonsite.io/user/login",
    "Nestlé Health Science": "https://live-61547-healthscience-corporate-me.pantheonsite.io/user/login",
    "Nestlé Professional": "https://www.nestleprofessionalmena.com/ae/en/HrpeJQiz4ta4o9PSB2YkHhR4/login",
    "NIDO": "https://www.nidolove.com/admin-login",
    "Purina": "https://live-dig0030543-petcare-purinattt-arabia.pantheonsite.io/user/login",
    "Starbucks": "https://live-dig0048100-nestleprofessional-starbucks-uae.pantheonsite.io/en/user/login",
    "Vital protiens": "https://live-dig0054909-nhs-vitalproteins-mena.pantheonsite.io/en/user/login",
    "Wyeth Nutrition Parenting Community": "https://parentingcommunity.wyethnutrition.com/user/login?admin=123"
}
