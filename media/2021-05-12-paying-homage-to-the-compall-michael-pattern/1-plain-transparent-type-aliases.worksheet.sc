object Units {
  type Kilometres = Double
  type Miles = Double
}

import Units._

class Booster() {
  def provideLaunchBoost(): Miles = 100
}

class Rocket(booster: Booster) {
  private var distance: Kilometres = 0

  def launch(): Unit = {
    // Kilometres and Miles are transparent. They are both Double so this bug slips through
    distance += booster.provideLaunchBoost()
  }

  def distanceTravelled: Kilometres = distance
}

val rocket: Rocket = new Rocket(new Booster())
rocket.launch();

// Will think it has travelled 100km rather than 160km
rocket.distanceTravelled
