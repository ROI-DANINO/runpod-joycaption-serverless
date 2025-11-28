# שינינו מ-runtime ל-devel כדי שיהיו כלים לקמפל את הספריות
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-devel

WORKDIR /app

# הוספתי build-essential כדי למנוע שגיאות התקנה
RUN apt-get update && apt-get install -y \
    git \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# שדרוג pip לפני ההתקנה (פותר הרבה בעיות)
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN git clone https://github.com/fpgaminer/joycaption.git

COPY handler.py .

CMD [ "python", "-u", "handler.py" ]
