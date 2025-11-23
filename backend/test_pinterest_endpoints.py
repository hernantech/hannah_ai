#!/usr/bin/env python3
"""
Test script for Pinterest API endpoints
This demonstrates how to use the three Pinterest endpoints
"""

import requests
import json

BASE_URL = "http://localhost:5000"
TEST_USER_ID = "test_user_123"

# IMPORTANT: Replace these with actual Pinterest credentials for testing
PINTEREST_CREDENTIALS = {
    "user_id": TEST_USER_ID,
    "pinterest_username": "your_pinterest_username",
    "pinterest_email": "your_pinterest_email@example.com",
    "pinterest_password": "your_pinterest_password"
}


def test_pinterest_login():
    """Test 1: Save Pinterest credentials"""
    print("\n" + "="*60)
    print("TEST 1: Saving Pinterest credentials")
    print("="*60)

    url = f"{BASE_URL}/api/pinterest/login"

    response = requests.post(url, json=PINTEREST_CREDENTIALS)

    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")

    return response.status_code == 200


def test_pinterest_status():
    """Test 2: Check Pinterest connection status"""
    print("\n" + "="*60)
    print("TEST 2: Checking Pinterest connection status")
    print("="*60)

    url = f"{BASE_URL}/api/pinterest/status"
    params = {"user_id": TEST_USER_ID}

    response = requests.get(url, params=params)

    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")

    data = response.json()
    if response.status_code == 200:
        status = data.get('pinterest_status')
        print(f"\n📌 Pinterest Status: {status.upper()}")

        if status == 'disconnected':
            print("   ℹ️  No Pinterest account linked yet. Run test_pinterest_login() first.")
        elif status == 'expired':
            print("   ⚠️  Pinterest session expired. Need to re-authenticate.")
        elif status == 'connected':
            print("   ✓ Pinterest connection is active!")

    return response.status_code == 200


def test_pinterest_boards():
    """Test 3: Get Pinterest mood boards"""
    print("\n" + "="*60)
    print("TEST 3: Fetching Pinterest mood boards")
    print("="*60)

    url = f"{BASE_URL}/api/pinterest/boards"
    params = {"user_id": TEST_USER_ID}

    response = requests.get(url, params=params)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n📊 Found {data.get('board_count', 0)} boards")

        boards = data.get('boards', [])
        if boards:
            print("\nBoards:")
            for i, board in enumerate(boards[:5], 1):  # Show first 5 boards
                print(f"\n  {i}. {board.get('name')}")
                print(f"     ID: {board.get('id')}")
                print(f"     Pins: {board.get('pin_count')}")
                print(f"     Description: {board.get('description', 'N/A')[:50]}...")
                print(f"     URL: {board.get('url')}")

            if len(boards) > 5:
                print(f"\n  ... and {len(boards) - 5} more boards")
        else:
            print("  No boards found")

        # Don't print full response (too long)
        print(f"\n(Full response omitted - {len(boards)} boards returned)")
    else:
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")

    return response.status_code == 200


def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "🧪 " * 20)
    print("PINTEREST API ENDPOINT TESTS")
    print("🧪 " * 20)

    # Test 1: Login (save credentials)
    success1 = test_pinterest_login()

    # Test 2: Check status
    success2 = test_pinterest_status()

    # Test 3: Get boards
    success3 = test_pinterest_boards()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"1. Login/Save Credentials: {'✓ PASS' if success1 else '✗ FAIL'}")
    print(f"2. Check Status: {'✓ PASS' if success2 else '✗ FAIL'}")
    print(f"3. Get Boards: {'✓ PASS' if success3 else '✗ FAIL'}")
    print("="*60)

    if all([success1, success2, success3]):
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    print("\n⚠️  IMPORTANT: Update PINTEREST_CREDENTIALS at the top of this file")
    print("    with your actual Pinterest username, email, and password\n")

    import sys
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name == "login":
            test_pinterest_login()
        elif test_name == "status":
            test_pinterest_status()
        elif test_name == "boards":
            test_pinterest_boards()
        else:
            print(f"Unknown test: {test_name}")
            print("Available tests: login, status, boards")
    else:
        run_all_tests()
