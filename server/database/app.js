const express = require('express');
const mongoose = require('mongoose');
const fs = require('fs');
const cors = require('cors');

const app = express();
const port = 3030;

app.use(cors());
app.use(require('body-parser').urlencoded({ extended: false }));

const reviews_data = JSON.parse(fs.readFileSync('reviews.json', 'utf8'));
const dealerships_data = JSON.parse(fs.readFileSync('dealerships.json', 'utf8'));

mongoose.connect('mongodb://mongo_db:27017/', { dbName: 'dealershipsDB' });

const Reviews = require('./review');
const Dealerships = require('./dealership');

// Инициализация базы: чистим и вставляем стартовые данные
Reviews.deleteMany({})
  .then(() => Reviews.insertMany(reviews_data.reviews))
  .catch(err => console.error('Seed Reviews error:', err));

Dealerships.deleteMany({})
  .then(() => Dealerships.insertMany(dealerships_data.dealerships))
  .catch(err => console.error('Seed Dealerships error:', err));

// Express route to home
app.get('/', async (req, res) => {
  res.send('Welcome to the Mongoose API');
});

// Express route to fetch all reviews
app.get('/fetchReviews', async (req, res) => {
  try {
    const documents = await Reviews.find();
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// Express route to fetch reviews by a particular dealer
app.get('/fetchReviews/dealer/:id', async (req, res) => {
  try {
    const documents = await Reviews.find({ dealership: req.params.id });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// Express route to fetch all dealerships
app.get('/fetchDealers', async (req, res) => {
  try {
    const docs = await Dealerships.find();
    res.json(docs);
  } catch (err) {
    console.error('fetchDealers error:', err);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

// Express route to fetch Dealers by a particular state
app.get('/fetchDealers/:state', async (req, res) => {
  try {
    const state = req.params.state;
    const docs = await Dealerships.find({
      state: { $regex: `^${state}$`, $options: 'i' },
    });
    res.json(docs);
  } catch (err) {
    console.error('fetchDealers/:state error:', err);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

// Express route to fetch dealer by a particular id
app.get('/fetchDealer/:id', async (req, res) => {
  try {
    const id = Number(req.params.id);
    if (Number.isNaN(id)) {
      return res.status(400).json({ error: 'Invalid id' });
    }
    const doc = await Dealerships.findOne({ id });
    if (!doc) {
      return res.status(404).json({ error: 'Dealer not found' });
    }
    res.json(doc);
  } catch (err) {
    console.error('fetchDealer/:id error:', err);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

// Express route to insert review
app.post('/insert_review', express.raw({ type: '*/*' }), async (req, res) => {
  try {
    const data = JSON.parse(req.body);
    const documents = await Reviews.find().sort({ id: -1 });
    const new_id = (documents[0] && documents[0].id);

    const review = new Reviews({
      id: new_id,
      name: data.name,
      dealership: data.dealership,
      review: data.review,
      purchase: data.purchase,
      purchase_date: data.purchase_date,
      car_make: data.car_make,
      car_model: data.car_model,
      car_year: data.car_year,
    });

    const savedReview = await review.save();
    res.json(savedReview);
  } catch (error) {
    console.error('insert_review error:', error);
    res.status(500).json({ error: 'Error inserting review' });
  }
});

// Start the Express server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
