import argparse
import sys
import time
import os
from pathlib import Path

# Ensure Windows console supports UTF-8 and ANSI escape codes
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    os.system("")

import config
from data_manager import DataManager
from posters.x_poster import XPoster
from posters.threads_poster import ThreadsPoster
from posters.engagement_bot import auto_reply_x, auto_reply_threads, TEMPLATES_FILE
import schedule

# ANSI Color formatting tokens
C_RESET   = "\033[0m"
C_BOLD    = "\033[1m"
C_CYAN    = "\033[96m"
C_GREEN   = "\033[92m"
C_YELLOW  = "\033[93m"
C_RED     = "\033[91m"
C_MAGENTA = "\033[95m"
C_WHITE   = "\033[97m"
C_GRAY    = "\033[90m"

def print_banner():
    """Prints a clean, professional CLI header without ASCII slop."""
    print(f"\n{C_CYAN}{C_BOLD}Social Promo Bot{C_RESET} {C_GRAY}v1.2.0{C_RESET}")
    print(f"{C_WHITE}Cross-Platform Publishing Engine for X (Twitter) & Threads{C_RESET}")
    print(f"{C_GRAY}Data-driven scheduler backed by Playwright persistent sessions{C_RESET}")
    print(f"{C_GRAY}{'-' * 66}{C_RESET}")

def show_excel_guide():
    """Displays standard column definitions and specifications for queue spreadsheets."""
    print("\n" + C_CYAN + "-" * 66 + C_RESET)
    print(f" {C_BOLD}SPREADSHEET QUEUE SPECIFICATION ({config.DEFAULT_EXCEL_PATH.name}){C_RESET}")
    print(C_CYAN + "-" * 66 + C_RESET)
    print(f"  {C_BOLD}1. ID{C_RESET}             : Unique integer identifier (e.g. 1, 2, 3...)")
    print(f"  {C_BOLD}2. PLATFORM{C_RESET}       : Target destination:")
    print(f"                      • {C_GREEN}both{C_RESET}    = Publish to both X and Threads")
    print(f"                      • {C_GREEN}x{C_RESET}       = X (Twitter) only")
    print(f"                      • {C_GREEN}threads{C_RESET} = Threads only")
    print(f"  {C_BOLD}3. SCHEDULE{C_RESET}       : Posting timestamp format: {C_YELLOW}YYYY-MM-DD HH:MM{C_RESET}")
    print(f"                      • Example : {C_WHITE}2026-09-20 14:30{C_RESET}")
    print(f"                      • {C_GRAY}Future datetime: Post waits until schedule arrives{C_RESET}")
    print(f"                      • {C_GRAY}Empty / blank  : Post dispatches immediately when run{C_RESET}")
    print(f"  {C_BOLD}4. CAPTION{C_RESET}        : Promotional text, product copy, links, and hashtags")
    print(f"  {C_BOLD}5. IMAGE{C_RESET}          : Relative or absolute local file path to media attachment:")
    print(f"                      • Example : {C_WHITE}sample_images/product.jpg{C_RESET}")
    print(f"                      • {C_GRAY}Empty / blank : Text-only post{C_RESET}")
    print(f"  {C_BOLD}6. STATUS{C_RESET}         : {C_GREEN}pending{C_RESET} (queued for execution). Automatically updated to")
    print(f"                      {C_CYAN}posted{C_RESET} on success, or {C_RED}failed{C_RESET} on error.")
    print(f"  {C_BOLD}7. POSTED_AT{C_RESET}      : Publication timestamp populated automatically by bot")
    print(f"  {C_BOLD}8. NOTES{C_RESET}          : Error message or execution diagnostic output")
    print(C_CYAN + "-" * 66 + C_RESET)

def process_pending_posts(data_manager: DataManager):
    """Processes posts that are marked pending and due for publication."""
    pending_posts = data_manager.get_pending_posts(check_schedule=True)
    timestamp_now = time.strftime('%H:%M:%S')

    if not pending_posts:
        print(f"{C_YELLOW}[{timestamp_now}] [INFO] No pending posts due for publication at this time.{C_RESET}")
        return

    print(f"\n{C_GREEN}[{timestamp_now}] [INFO] Found {len(pending_posts)} post(s) ready for execution...{C_RESET}")

    for item in pending_posts:
        post_id = item["id"]
        caption = item.get("caption", "").strip()
        image_path = item.get("image_path", "").strip()
        platform = str(item.get("platform", "both")).strip().lower()
        jadwal = item.get("jadwal", "Immediate")

        if not caption:
            print(f"{C_GRAY}[WARN] Post ID #{post_id} skipped: Caption content is empty.{C_RESET}")
            continue

        print("\n" + C_CYAN + "-" * 56 + C_RESET)
        print(f" {C_BOLD}Processing Post ID :{C_RESET} #{post_id}")
        print(f" {C_BOLD}Target Platform   :{C_RESET} {C_MAGENTA}{platform.upper()}{C_RESET}")
        print(f" {C_BOLD}Schedule Mode     :{C_RESET} {C_YELLOW}{jadwal}{C_RESET}")
        summary_cap = f"{caption[:65]}..." if len(caption) > 65 else caption
        print(f" {C_BOLD}Caption Content   :{C_RESET} {summary_cap}")
        if image_path:
            print(f" {C_BOLD}Media Attachment  :{C_RESET} {C_YELLOW}{image_path}{C_RESET}")
        print(C_CYAN + "-" * 56 + C_RESET)

        success_x = True
        success_threads = True
        error_notes = []

        # 1. Dispatch to X (Twitter)
        if platform in ["x", "both"]:
            print(f"{C_CYAN}[INFO] Launching browser context for X (Twitter)...{C_RESET}")
            x_poster = XPoster()
            try:
                x_poster.start_browser()
                if not x_poster.post(caption=caption, image_path=image_path):
                    success_x = False
                    error_notes.append("X post failed")
            except Exception as e:
                success_x = False
                error_notes.append(f"X exception: {e}")
            finally:
                x_poster.stop_browser()

            if platform == "both":
                time.sleep(10)

        # 2. Dispatch to Threads
        if platform in ["threads", "both"]:
            print(f"{C_CYAN}[INFO] Launching browser context for Threads...{C_RESET}")
            threads_poster = ThreadsPoster()
            try:
                threads_poster.start_browser()
                if not threads_poster.post(caption=caption, image_path=image_path):
                    success_threads = False
                    error_notes.append("Threads post failed")
            except Exception as e:
                success_threads = False
                error_notes.append(f"Threads exception: {e}")
            finally:
                threads_poster.stop_browser()

        # Update status in spreadsheet
        all_success = (success_x if platform in ["x", "both"] else True) and \
                      (success_threads if platform in ["threads", "both"] else True)

        if all_success:
            data_manager.mark_post_status(post_id, "posted", note="Published successfully")
            print(f"{C_GREEN}[OK] Post #{post_id} published successfully. Status updated to 'posted'.{C_RESET}")
        else:
            note_str = ", ".join(error_notes)
            data_manager.mark_post_status(post_id, "failed", note=note_str)
            print(f"{C_RED}[FAIL] Post #{post_id} failed: {note_str}{C_RESET}")

        delay = config.POST_INTERVAL_MIN
        print(f"{C_GRAY}[INFO] Waiting {delay}s safety delay before next queued item...{C_RESET}\n")
        time.sleep(delay)

def check_accounts_login():
    """Validates whether authenticated sessions exist for X and Threads."""
    print(f"\n{C_CYAN}--- SESSION VERIFICATION ---{C_RESET}")
    
    print("[1/2] Verifying X (Twitter) session...")
    xp = XPoster(headless=True)
    try:
        xp.start_browser()
        is_x_in = xp.is_logged_in()
        status_x = f"{C_GREEN}[ACTIVE / AUTHENTICATED]{C_RESET}" if is_x_in else f"{C_RED}[INACTIVE / NOT SIGNED IN]{C_RESET}"
        print(f"      Status: {status_x}")
    except Exception as e:
        print(f"      {C_RED}Error verifying X: {e}{C_RESET}")
    finally:
        xp.stop_browser()

    print("[2/2] Verifying Threads session...")
    tp = ThreadsPoster(headless=True)
    try:
        tp.start_browser()
        is_th_in = tp.is_logged_in()
        status_th = f"{C_GREEN}[ACTIVE / AUTHENTICATED]{C_RESET}" if is_th_in else f"{C_RED}[INACTIVE / NOT SIGNED IN]{C_RESET}"
        print(f"      Status: {status_th}")
    except Exception as e:
        print(f"      {C_RED}Error verifying Threads: {e}{C_RESET}")
    finally:
        tp.stop_browser()

def open_excel_file():
    """Opens the active spreadsheet file with the default host application."""
    file_path = str(config.DEFAULT_EXCEL_PATH.resolve())
    print(f"{C_GREEN}[INFO] Opening spreadsheet file: {file_path}{C_RESET}")
    try:
        os.startfile(file_path)
    except Exception as e:
        print(f"{C_RED}[ERROR] Failed to open spreadsheet automatically: {e}{C_RESET}")

def open_templates_file():
    """Opens the reply_templates.txt file with the default editor."""
    file_path = str(TEMPLATES_FILE.resolve())
    print(f"{C_GREEN}[INFO] Opening reply templates file: {file_path}{C_RESET}")
    try:
        os.startfile(file_path)
    except Exception as e:
        print(f"{C_RED}[ERROR] Failed to open template file: {e}{C_RESET}")

def interactive_menu(data_manager: DataManager):
    """Presents a clean, structured CLI control menu."""
    while True:
        print_banner()

        print(f" {C_CYAN}[1] ACCOUNT & SESSION MANAGEMENT{C_RESET}")
        print(f"   {C_WHITE}1.{C_RESET} Setup Account Login        {C_GRAY}(Interactive browser sign-in){C_RESET}")
        print(f"   {C_WHITE}2.{C_RESET} Verify Session Status      {C_GRAY}(Check active session cookies){C_RESET}")
        print()
        print(f" {C_MAGENTA}[2] CONTENT QUEUE & SCHEDULING{C_RESET}")
        print(f"   {C_WHITE}3.{C_RESET} View Pending Queue         {C_GRAY}(Inspect scheduled posts){C_RESET}")
        print(f"   {C_WHITE}4.{C_RESET} Open Queue Spreadsheet     {C_GRAY}(Launch promo_data.xlsx){C_RESET}")
        print(f"   {C_WHITE}5.{C_RESET} View Queue Format Guide    {C_GRAY}(Column specs & instructions){C_RESET}")
        print()
        print(f" {C_GREEN}[3] EXECUTION & AUTOMATION{C_RESET}")
        print(f"   {C_WHITE}6.{C_RESET} Publish Ready Posts Now    {C_GRAY}(Process due items immediately){C_RESET}")
        print(f"   {C_WHITE}7.{C_RESET} Start Scheduler Daemon     {C_GRAY}(Periodic background monitor){C_RESET}")
        print(f"   {C_WHITE}8.{C_RESET} Keyword Auto-Engagement    {C_GRAY}(Search keywords & auto-reply){C_RESET}")
        print(f"   {C_WHITE}9.{C_RESET} Edit Reply Templates       {C_GRAY}(Configure reply_templates.txt){C_RESET}")
        print()
        print(f" {C_RED}[4] EXIT{C_RESET}")
        print(f"   {C_WHITE}0.{C_RESET} Exit Application")
        print(f"{C_GRAY}{'-' * 66}{C_RESET}")

        choice = input(f" {C_YELLOW}Select an option (0-9): {C_RESET}").strip()

        if choice == "1":
            import setup_accounts
            setup_accounts.main()
        elif choice == "2":
            check_accounts_login()
        elif choice == "3":
            all_posts = data_manager.get_all_pending_summary()
            print(f"\n{C_CYAN}[Queue Inspector] Total {len(all_posts)} post(s) marked 'pending':{C_RESET}")
            if not all_posts:
                print(f"{C_YELLOW}  (No queued posts found in spreadsheet){C_RESET}")
            for p in all_posts:
                img_info = f" | Media: {p['image_path']}" if p.get("image_path") else " | (Text only)"
                sched_info = f" | Schedule: {p['jadwal']}"
                print(f"  {C_BOLD}• ID #{p['id']} [{p['platform'].upper()}]{C_RESET}{sched_info}{img_info}\n    {C_GRAY}Caption: {p['caption'][:80]}...{C_RESET}\n")
        elif choice == "4":
            open_excel_file()
        elif choice == "5":
            show_excel_guide()
        elif choice == "6":
            print(f"\n{C_YELLOW}[CONFIRMATION] Bot will process all pending items whose schedule is due.{C_RESET}")
            confirm = input("Proceed with publishing? (y/n): ").strip().lower()
            if confirm == "y":
                process_pending_posts(data_manager)
        elif choice == "7":
            interval_str = input("\nEnter scheduler polling interval in minutes (e.g. 15 or 30): ").strip()
            try:
                minutes = int(interval_str)
                if minutes <= 0:
                    raise ValueError
                print(f"\n{C_GREEN}[INFO] Scheduler active. Polling queue every {minutes} minute(s)...{C_RESET}")
                print(f"{C_GRAY}[INFO] Due items will be dispatched automatically.{C_RESET}")
                print(f"{C_GRAY}[INFO] Press Ctrl+C to return to main menu.{C_RESET}\n")
                process_pending_posts(data_manager)
                schedule.every(minutes).minutes.do(process_pending_posts, data_manager=data_manager)
                while True:
                    schedule.run_pending()
                    time.sleep(10)
            except KeyboardInterrupt:
                print(f"\n{C_YELLOW}[INFO] Scheduler paused.{C_RESET}")
                schedule.clear()
            except ValueError:
                print(f"{C_RED}[ERROR] Invalid interval. Please enter a positive integer.{C_RESET}")
        elif choice == "8":
            print("\n" + C_CYAN + "-" * 56 + C_RESET)
            print(f"  {C_BOLD}KEYWORD ENGAGEMENT & AUTO-REPLY{C_RESET}")
            print(C_CYAN + "-" * 56 + C_RESET)
            print("  1. Target X (Twitter) only")
            print("  2. Target Threads only")
            print("  3. Target both platforms (X & Threads)")
            print("  0. Back to Main Menu")
            target_plat = input("\n  Select target platform (1/2/3/0): ").strip()

            if target_plat in ["1", "2", "3"]:
                kw = input("\n  Enter search query or hashtag (e.g., #gadget, productivity tips): ").strip()
                if not kw:
                    print(f"{C_RED}  [ERROR] Keyword cannot be empty.{C_RESET}")
                    continue

                target_count_str = input("  Max replies to post (recommended 3-5): ").strip()
                try:
                    target_count = int(target_count_str)
                    if target_count <= 0:
                        target_count = 3
                except ValueError:
                    target_count = 3

                print(f"\n{C_CYAN}  [INFO] Querying latest posts matching: '{kw}'{C_RESET}")
                print(f"{C_CYAN}  [INFO] Replies will be randomly selected from 'reply_templates.txt'.{C_RESET}")
                confirm_engagement = input("\n  Start auto-reply job now? (y/n): ").strip().lower()
                if confirm_engagement == "y":
                    if target_plat in ["1", "3"]:
                        auto_reply_x(keyword=kw, max_replies=target_count)
                    if target_plat in ["2", "3"]:
                        auto_reply_threads(keyword=kw, max_replies=target_count)
        elif choice == "9":
            open_templates_file()
        elif choice == "0":
            print(f"\n{C_GREEN}Social Promo Bot session terminated. Goodbye.{C_RESET}\n")
            break
        else:
            print(f"\n{C_RED}[ERROR] Invalid choice. Please enter a number between 0 and 9.{C_RESET}")

        input(f"\n{C_GRAY}Press [ENTER] to return to menu...{C_RESET}")

def main():
    parser = argparse.ArgumentParser(
        description="Social Promo Bot - Automated Cross-Platform Publishing Engine for X & Threads"
    )
    parser.add_argument("--run-now", action="store_true", help="Process ready queue items immediately")
    parser.add_argument("--schedule", type=int, metavar="MINUTES", help="Run polling scheduler every N minutes")
    parser.add_argument("--check-login", action="store_true", help="Verify session authentication status")
    parser.add_argument("--test-excel", action="store_true", help="Inspect spreadsheet pending queue")

    args = parser.parse_args()
    data_manager = DataManager()

    if args.test_excel:
        posts = data_manager.get_all_pending_summary()
        print(f"\n[Queue Inspector] Total {len(posts)} item(s) marked 'pending':")
        for p in posts:
            print(f"- ID #{p['id']} [{p['platform'].upper()}]: {p['caption'][:60]}... (Schedule: {p['jadwal']})")
        return

    if args.check_login:
        check_accounts_login()
        return

    if args.run_now:
        process_pending_posts(data_manager)
        return

    if args.schedule:
        minutes = args.schedule
        print(f"[INFO] Scheduler active. Polling queue every {minutes} minute(s). Press Ctrl+C to stop.")
        process_pending_posts(data_manager)
        schedule.every(minutes).minutes.do(process_pending_posts, data_manager=data_manager)
        while True:
            schedule.run_pending()
            time.sleep(10)

    # Launch interactive CLI
    interactive_menu(data_manager)

if __name__ == "__main__":
    main()
