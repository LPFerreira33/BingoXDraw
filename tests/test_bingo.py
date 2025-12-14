"""
Comprehensive test suite for BingoXDraw bingo number management system.

Tests focus on the core logic and state management of the bingo game,
including number withdrawal, cancellation, addition, checking for bingo,
and file persistence. These tests do not cover GUI rendering which requires
a display environment.

Test categories:
- Withdraw/Cancel operations: Number selection and reversal
- Add Number: Adding new numbers to the available pool
- Check Bingo: Verifying if selected numbers match withdrawn numbers
- File Persistence: Saving and loading game state
- Integration Scenarios: Real-world game workflows
"""

import pytest
import sys
import tempfile
import os
import pickle
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bingo_utils import (
    save_numbers_to_file,
    load_numbers_from_file,
    withdraw_number,
    cancel_withdraw,
    add_number,
    check_bingo,
)


# ============================================================================
# WITHDRAW NUMBER TESTS
# ============================================================================

class TestWithdrawNumber:
    """Tests for withdraw_number functionality"""

    def test_state_consistency_after_withdraw(self):
        """Test state consistency after withdrawal"""
        bingo_numbers = [1, 2, 3, 4, 5]
        withdrawn_numbers = []
        
        # Withdraw
        withdrawn = withdraw_number(bingo_numbers, withdrawn_numbers)
        
        # Check consistency
        assert withdrawn is not None
        assert withdrawn in withdrawn_numbers
        assert withdrawn not in bingo_numbers
        assert withdrawn in [1, 2, 3, 4, 5]
        assert set(bingo_numbers).union(set(withdrawn_numbers)) == {1, 2, 3, 4, 5}
        assert len(bingo_numbers) == 4
        assert len(withdrawn_numbers) == 1
        
    def test_withdraw_number_from_empty_list(self):
        """Test withdrawing when no numbers are available - should return None"""
        bingo_numbers = []
        withdrawn_numbers = []
        
        withdrawn = withdraw_number(bingo_numbers, withdrawn_numbers)
        
        assert withdrawn is None
        assert len(bingo_numbers) == 0
        assert len(withdrawn_numbers) == 0
        
    def test_rapid_withdrawals(self):
        """Test rapid consecutive withdrawals"""
        bingo_numbers = list(range(1, 101))
        withdrawn_numbers = []
        
        for _ in range(50):
            withdraw_number(bingo_numbers, withdrawn_numbers)
        
        assert len(bingo_numbers) == 50
        assert len(withdrawn_numbers) == 50
        assert len(set(withdrawn_numbers)) == 50  # All unique


# ============================================================================
# CANCEL WITHDRAW TESTS
# ============================================================================

class TestCancelWithdraw:
    """Tests for cancel_withdraw functionality"""

    def test_state_consistency_after_cancel(self):
        """Test state consistency after cancel"""
        bingo_numbers = [1, 2, 3]
        withdrawn_numbers = [4, 5]
        
        # Cancel
        canceled = cancel_withdraw(bingo_numbers, withdrawn_numbers)
        
        # Check consistency
        assert canceled is not None
        assert canceled in bingo_numbers
        assert canceled not in withdrawn_numbers
        assert canceled == 5
        assert bingo_numbers == [1, 2, 3, 5]
        assert withdrawn_numbers == [4]

    def test_cancel_withdraw_event_without_withdrawals(self):
        """Test cancel event when no withdrawals exist"""
        bingo_numbers = [1, 2, 3]
        withdrawn_numbers = []
        
        # Simulate cancel event
        result = cancel_withdraw(bingo_numbers, withdrawn_numbers)
        
        # No change should occur
        assert result is None
        assert bingo_numbers == [1, 2, 3]
        assert withdrawn_numbers == []

    def test_cancel_multiple_withdrawals(self):
        """Test canceling multiple withdrawals in sequence"""
        bingo_numbers = []
        withdrawn_numbers = [1, 2, 3]
        
        # Cancel first withdrawal
        canceled1 = cancel_withdraw(bingo_numbers, withdrawn_numbers)
        assert canceled1 == 3
        assert withdrawn_numbers == [1, 2]
        assert bingo_numbers == [3]
        
        # Cancel second withdrawal
        canceled2 = cancel_withdraw(bingo_numbers, withdrawn_numbers)
        assert canceled2 == 2
        assert withdrawn_numbers == [1]
        assert bingo_numbers == [2, 3]
        
        # Cancel third withdrawal
        canceled3 = cancel_withdraw(bingo_numbers, withdrawn_numbers)
        assert canceled3 == 1
        assert withdrawn_numbers == []
        assert bingo_numbers == [1, 2, 3]
        
        # Try to cancel from empty list
        canceled4 = cancel_withdraw(bingo_numbers, withdrawn_numbers)
        assert canceled4 is None
        assert withdrawn_numbers == []
        assert bingo_numbers == [1, 2, 3]


# ============================================================================
# ADD NUMBER TESTS
# ============================================================================

class TestAddNumber:
    """Tests for add_number functionality"""

    def test_state_consistency_after_add(self):
        """Test state consistency after adding number"""
        bingo_numbers = [1, 2, 3]
        withdrawn_numbers = [4, 5]
        
        success, message = add_number(bingo_numbers, withdrawn_numbers, 100)
        
        assert success
        assert withdrawn_numbers == [4, 5]
        assert bingo_numbers == [1, 2, 3, 100]
        assert message == "Number 100 successfully added."

    def test_add_number_maintains_sort(self):
        """Test that list remains sorted after adding a number"""
        bingo_numbers = [1, 3, 5]
        withdrawn_numbers = []
        
        success, message = add_number(bingo_numbers, withdrawn_numbers, 2)
        
        assert success
        assert bingo_numbers == [1, 2, 3, 5]
        assert withdrawn_numbers == []
        assert message == "Number 2 successfully added."
        
    def test_add_number_to_empty_list(self):
        """Test adding a number to an empty list"""
        bingo_numbers = []
        withdrawn_numbers = []
        
        success, message = add_number(bingo_numbers, withdrawn_numbers, 10)
        
        assert success
        assert bingo_numbers == [10]
        assert withdrawn_numbers == []
        assert message == "Number 10 successfully added."
        
    def test_add_existing_bingo_number(self):
        """Test adding a number that already exists in bingo numbers"""
        bingo_numbers = [1, 2, 3]
        withdrawn_numbers = [4, 5]
        
        success, message = add_number(bingo_numbers, withdrawn_numbers, 2)
        
        # Adding existing number should fail
        assert not success
        assert bingo_numbers == [1, 2, 3]
        assert withdrawn_numbers == [4, 5]
        assert message == "Number 2 is already in the available numbers list."
        
    def test_add_existing_withdrawn_number(self):
        """Test adding a number that already exists in withdrawn numbers"""
        bingo_numbers = [1, 2, 3]
        withdrawn_numbers = [4, 5]
        
        success, message = add_number(bingo_numbers, withdrawn_numbers, 4)
        
        # Adding existing withdrawn number should fail
        assert not success
        assert bingo_numbers == [1, 2, 3]
        assert withdrawn_numbers == [4, 5]
        assert message == "Number 4 is already in the withdrawn numbers list."
        
    def test_add_multiple_numbers(self):
        """Test adding multiple numbers sequentially"""
        bingo_numbers = [5]
        withdrawn_numbers = []
        
        add_number(bingo_numbers, withdrawn_numbers, 2)
        
        assert bingo_numbers == [2, 5]
        assert withdrawn_numbers == []
        
        add_number(bingo_numbers, withdrawn_numbers, 8)
        
        assert bingo_numbers == [2, 5, 8]
        assert withdrawn_numbers == []
        
        add_number(bingo_numbers, withdrawn_numbers, 1)
        
        assert bingo_numbers == [1, 2, 5, 8]
        assert withdrawn_numbers == []


# ============================================================================
# CHECK BINGO TESTS
# ============================================================================

class TestCheckBingo:
    """Tests for check_bingo functionality"""

    def test_check_bingo_all_withdrawn(self):
        """Test check numbers event when all are withdrawn"""
        numbers_to_check = [1, 2, 3]
        withdrawn_numbers = [1, 2, 3, 4, 5]
        
        # Simulate check event
        results, is_bingo = check_bingo(numbers_to_check, withdrawn_numbers)
        
        assert is_bingo is True
        assert all(r == "Withdrawn" for r in results)

    def test_check_bingo_none_withdrawn(self):
        """Test check numbers event when none are withdrawn"""
        numbers_to_check = [1, 2, 3]
        withdrawn_numbers = [10, 11, 12]
        
        # Simulate check event
        results, is_bingo = check_bingo(numbers_to_check, withdrawn_numbers)
        
        assert is_bingo is False
        assert all(r == "Not Withdrawn" for r in results)
        
    def test_check_bingo_partial_withdrawn(self):
        """Test checking numbers when only some are withdrawn - should return False"""
        numbers_to_check = [1, 2, 3]
        withdrawn_numbers = [1, 5, 6]
        
        results, is_bingo = check_bingo(numbers_to_check, withdrawn_numbers)
        
        assert is_bingo is False
        assert results == ["Withdrawn", "Not Withdrawn", "Not Withdrawn"]

    def test_check_bingo_single_number_withdrawn(self):
        """Test checking a single number that is withdrawn"""
        numbers_to_check = [42]
        withdrawn_numbers = [42]
        
        results, is_bingo = check_bingo(numbers_to_check, withdrawn_numbers)
        
        assert is_bingo is True
        assert results == ["Withdrawn"]
        
    def test_check_bingo_empty_withdrawn_list(self):
        """Test checking when no numbers have been withdrawn"""
        numbers_to_check = [1, 2, 3]
        withdrawn_numbers = []
        
        results, is_bingo = check_bingo(numbers_to_check, withdrawn_numbers)
        
        assert is_bingo is False
        assert all(r == "Not Withdrawn" for r in results)
        
    def test_check_bingo_doesnt_modify_lists(self):
        """Test that check_bingo doesn't modify input lists"""
        numbers_to_check = [1, 2, 3]
        withdrawn_numbers = [2, 3]
        
        original_check = numbers_to_check.copy()
        original_withdrawn = withdrawn_numbers.copy()
        
        check_bingo(numbers_to_check, withdrawn_numbers)
        
        assert numbers_to_check == original_check
        assert withdrawn_numbers == original_withdrawn


# ============================================================================
# FILE PERSISTENCE TESTS
# ============================================================================

class TestFilePersistence:
    """Test file operations and persistence"""

    def test_save_on_exit(self):
        """Test that game state is saved on exit"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "bingo_data.pkl")
            bingo_numbers = [1, 2, 3]
            withdrawn_numbers = [4]
            
            # Simulate save on exit
            save_numbers_to_file(filepath, bingo_numbers, withdrawn_numbers)
            
            # Verify file exists
            assert os.path.exists(filepath)

    def test_load_on_startup(self):
        """Test that game state is loaded on startup"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "bingo_data.pkl")
            bingo_numbers = [1, 2, 3]
            withdrawn_numbers = [4]
            
            # Save state
            save_numbers_to_file(filepath, bingo_numbers, withdrawn_numbers)
            
            # Load state
            loaded_bingo, loaded_withdrawn = load_numbers_from_file(filepath, 0)
            
            assert loaded_bingo == bingo_numbers
            assert loaded_withdrawn == withdrawn_numbers

    def test_load_default_when_no_file(self):
        """Test that default state is loaded when file doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "nonexistent.pkl")
            max_number = 90
            
            # Load (file doesn't exist)
            bingo_numbers, withdrawn_numbers = load_numbers_from_file(filepath, max_number)
            
            assert bingo_numbers == list(range(1, max_number + 1))
            assert withdrawn_numbers == []

    def test_save_empty_lists(self):
        """Test saving empty bingo and withdrawn lists"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "empty_bingo.pkl")
            bingo_numbers = []
            withdrawn_numbers = []
            
            save_numbers_to_file(filepath, bingo_numbers, withdrawn_numbers)
            loaded_bingo, loaded_withdrawn = load_numbers_from_file(filepath, 0)
            
            assert loaded_bingo == []
            assert loaded_withdrawn == []
            
    def test_save_large_list(self):
        """Test saving and loading a large list of numbers"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "large_bingo.pkl")
            bingo_numbers = list(range(1, 1001))  # 1000 numbers
            withdrawn_numbers = list(range(1, 101))  # 100 withdrawn
            
            save_numbers_to_file(filepath, bingo_numbers, withdrawn_numbers)
            loaded_bingo, loaded_withdrawn = load_numbers_from_file(filepath, 0)
            
            assert loaded_bingo == bingo_numbers
            assert loaded_withdrawn == withdrawn_numbers
            
    def test_file_integrity_with_pickle(self):
        """Test that file is properly created and formatted"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "integrity_test.pkl")
            bingo_numbers = [5, 10, 15]
            withdrawn_numbers = [5]
            
            save_numbers_to_file(filepath, bingo_numbers, withdrawn_numbers)
            
            # Verify file exists
            assert os.path.exists(filepath)
            
            # Manually read and verify pickle format
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                assert isinstance(data, dict)
                assert 'bingo_numbers' in data
                assert 'withdrawn_numbers' in data
                
                
# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegrationScenarios:
    """Integration tests simulating real game scenarios"""

    def test_complete_game_scenario(self):
        """Test a complete game scenario: create, withdraw, check"""
        # Initialize
        bingo_numbers = [1, 2, 3, 4, 5]
        withdrawn_numbers = []
        
        # Withdraw some numbers
        first_number = withdraw_number(bingo_numbers, withdrawn_numbers)
        second_number = withdraw_number(bingo_numbers, withdrawn_numbers)
        
        assert len(bingo_numbers) == 3
        assert len(withdrawn_numbers) == 2
        
        # Check if we have bingo
        results, is_bingo = check_bingo([first_number, second_number], withdrawn_numbers)
        assert is_bingo is True
        assert results == ["Withdrawn", "Withdrawn"]
        assert first_number in [1, 2, 3, 4, 5]
        assert second_number in [1, 2, 3, 4, 5]
        assert first_number != second_number
        assert first_number in withdrawn_numbers
        assert second_number in withdrawn_numbers
        assert first_number not in bingo_numbers
        assert second_number not in bingo_numbers
        assert len(bingo_numbers) == 3
        assert len(withdrawn_numbers) == 2
        assert set(bingo_numbers).union(set(withdrawn_numbers)) == {1, 2, 3, 4, 5}

    def test_withdraw_cancel_withdraw_cycle(self):
        """Test withdrawing, canceling, and withdrawing again"""
        bingo_numbers = [1, 2, 3, 4, 5]
        withdrawn_numbers = []
        initial_count = len(bingo_numbers)
        
        # Withdraw a number
        first_withdraw = withdraw_number(bingo_numbers, withdrawn_numbers)
        
        # Cancel it
        canceled = cancel_withdraw(bingo_numbers, withdrawn_numbers)
        assert canceled == first_withdraw
        assert withdrawn_numbers == []
        assert bingo_numbers == [1, 2, 3, 4, 5]
        
        # Withdraw again
        second_withdraw = withdraw_number(bingo_numbers, withdrawn_numbers)
        assert second_withdraw is not None
        assert len(bingo_numbers) == initial_count - 1

    def test_add_then_withdraw(self):
        """Test adding a number then withdrawing it"""
        bingo_numbers = [1, 2, 3]
        withdrawn_numbers = []
        
        # Add a number
        success, message = add_number(bingo_numbers, withdrawn_numbers, 10)
        assert success
        assert 10 in bingo_numbers
        
        # Keep withdrawing until we get the new number
        max_attempts = 100
        for _ in range(max_attempts):
            withdrawn = withdraw_number(bingo_numbers, withdrawn_numbers)
            if withdrawn == 10:
                break
        
        assert withdrawn == 10
        assert 10 not in bingo_numbers
        assert 10 in withdrawn_numbers
        assert len(bingo_numbers) + len(withdrawn_numbers) == 4
        assert set(bingo_numbers).union(set(withdrawn_numbers)) == {1, 2, 3, 10}

    def test_withdraw_all_then_cancel_all(self):
        """Test withdrawing all numbers then canceling all"""
        bingo_numbers = [1, 2, 3]
        withdrawn_numbers = []
        original_count = len(bingo_numbers)
        
        # Withdraw all
        for _ in range(original_count):
            withdraw_number(bingo_numbers, withdrawn_numbers)
        
        assert len(bingo_numbers) == 0
        assert len(withdrawn_numbers) == original_count
        
        # Cancel all
        for _ in range(original_count):
            cancel_withdraw(bingo_numbers, withdrawn_numbers)
        
        assert bingo_numbers == [1, 2, 3]
        assert withdrawn_numbers == []