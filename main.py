import tracker

def get_iss_location():
    # Fetch coordinates using the shared tracker module
    lat, lon, error = tracker.get_iss_location()
    if error:
        print(f"Error fetching ISS data: {error}")
        return

    print(f"\nISS Position: {lat:.4f}, {lon:.4f}")

    # Fetch location details using the shared tracker module
    details = tracker.get_location_details(lat, lon)

    # 1. Precise Address (if on/near land)
    precise = details.get('precise_location')
    if precise:
        print("\n--- Precise Location (On/Near Land) ---")
        print(f"Address: {precise.get('address')}")
        city = precise.get('city')
        state = precise.get('state')
        country = precise.get('country')
        if city: print(f"City: {city}")
        if state: print(f"State: {state}")
        if country: print(f"Country: {country}")
    else:
        print("\n--- Over Ocean or Remote Area ---")
        ocean = details.get('ocean')
        if ocean:
            print(f"Body of Water: {ocean}")

    # 2. Nearest Land (offline search fallback)
    nearest = details.get('nearest_land')
    if nearest:
        place_name = nearest.get('place_name')
        admin1 = nearest.get('admin1')
        cc = nearest.get('cc')
        distance = nearest.get('distance')

        print(f"\nNearest Land Mass: {distance:.2f} km away")
        print(f"Location: {place_name}, {admin1}, {cc}")

        if not precise:
            # If we didn't get a precise address, this is our best guess
            print(f"Status: The ISS is currently over water or remote terrain, approximately {distance:.0f}km from {place_name}, {cc}.")

if __name__ == "__main__":
    get_iss_location()
