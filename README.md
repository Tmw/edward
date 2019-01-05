<img src="meta/edward_logo.svg" width="300" />
<br />
<br />

[![Build Status](https://travis-ci.com/Tmw/edward.svg?branch=master)](https://travis-ci.com/Tmw/edward)

**Edward Scissorhands** is a slackbot that utilizes machinelearning to remove the background of any uploaded image. Edward works best with images containing people.

## Edward's brain 🧠

Edward depends on a pre-trained Tensorflow model as explained in this [blogpost](https://towardsdatascience.com/background-removal-with-deep-learning-c4f2104b3157). The fully pre-trained model can be found over their Gitlab [Repository](https://gitlab.com/fast-science/background-removal-server/tree/master/webapp/model).

_Note; the model in this repository is merely a mirror. In both cases; pull using [git lfs](https://git-lfs.github.com/)._

## Running tests

```bash
make test
```

## Running Edward from source

Make sure you fill in the missing pieces in your `.env` file and simply run:

```bash
make run
```

> _if you don't have an .env file, create one by looking at the example (`.example.env`)_

## Environment Variables

| Variable    | Type   | Meaning                        |
| ----------- | ------ | ------------------------------ |
| SLACK_TOKEN | String | Your slack token               |
| THREADS     | Int    | How many threads do we reserve |
