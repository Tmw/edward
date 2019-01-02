# Edward 🤖 ✂️

Edward Scissorhands is a slackbot that utilizes machinelearning to remove the background of any uploaded image. Edward works best with images containing people.

# Edward's brain 🧠

Edward depends on a pre-trained Tensorflow model as explained in this [blogpost](https://towardsdatascience.com/background-removal-with-deep-learning-c4f2104b3157). The fully pre-trained model can be found over their Gitlab [Repository](https://gitlab.com/fast-science/background-removal-server/tree/master/webapp/model).

_Note; the model in this repository is merely a mirror. In both cases; pull using [git lfs](https://git-lfs.github.com/)._

# Running tests

_Using Make:_

```bash
make test
```

_or without make:_

```bash
python -m unittest discover -s tests
```

# Running Edward

```bash
SLACK_TOKEN="YOUR_SLACK_TOKEN" \
THREADS=2 \
python main.py
```

# Environment Variables

| Variable    | Type   | Meaning                        |
| ----------- | ------ | ------------------------------ |
| SLACK_TOKEN | String | Your slack token               |
| THREADS     | Int    | How many threads do we reserve |
