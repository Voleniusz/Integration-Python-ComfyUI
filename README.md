# ComfyUI Prompt GUI

Aplikacja okienkowa do generowania obrazów przez ComfyUI na podstawie promptu wpisanego przez użytkownika.

## Wymagania
- Python 3.10+
- Zainstalowane biblioteki z `requirements.txt`
- Uruchomiony ComfyUI lokalnie (domyślnie na http://127.0.0.1:8188)

## Instalacja
1. Zainstaluj wymagane biblioteki:
   ```bash
   pip install -r requirements.txt
   ```
2. Upewnij się, że ComfyUI jest uruchomiony.

## Uruchomienie
```bash
python main.py
```

## Działanie
- Wpisz prompt w oknie aplikacji i kliknij "Generuj obraz".
- Wygenerowany obraz pojawi się w oknie.

## Uwaga
- Jeśli Twój ComfyUI działa na innym porcie niż 8188, zmień wartość `COMFY_API_URL` w pliku `main.py`. 