object Units {
  final case class Kilometers(value: Double)
  final case class Miles(value: Double)

  def add(km1: Kilometers, km2: Kilometers): Kilometers = Kilometers(km1.value + km2.value)
  def toKilometers(miles: Miles): Kilometers = Kilometers(miles.value * 1.6)
}

import Units._

class Booster() {
  def provideLaunchBoost(): Miles = Miles(100)
}

class Rocket(booster: Booster) {
  private var distance: Kilometers = Kilometers(0)

  def launch(): Unit = {
    // Kilometers and Miles are different types. So compiler prevents the previous bug
    val launchBoost: Kilometers = toKilometers(booster.provideLaunchBoost())
    distance = add(distance, launchBoost)
  }

  def distanceTravelled: Kilometers = distance
}

val rocket: Rocket = new Rocket(new Booster())
rocket.launch();

// Will represent the correct distance travelled
rocket.distanceTravelled
