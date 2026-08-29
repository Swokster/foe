import subprocess
import sys


def main():
  # Запускаем streamlit run app.py локально
  cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]
  try:
    subprocess.run(cmd)
  except KeyboardInterrupt:
    print("\nСервер остановлен пользователем.")


if __name__ == "__main__":
  main()