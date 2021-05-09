object Units {
  final case class Kilometres(value: Double)
  final case class Miles(value: Double)

  def add(km1: Kilometres, km2: Kilometres): Kilometres = Kilometres(km1.value + km2.value)
  def toKm(miles: Miles): Kilometres = Kilometres(miles.value * 1.6)
}

import Units._

class Booster() {
  def provideLaunchBoost(): Miles = Miles(100)
}

class Rocket(booster: Booster) {
  private var distance: Kilometres = Kilometres(0)

  def launch(): Unit = {
    // Kilometres and Miles are different types. So compiler prevents the previous bug
    val launchBoost: Kilometres = toKm(booster.provideLaunchBoost())
    distance = add(distance, launchBoost)
  }

  def distanceTravelled: Kilometres = distance
}

val rocket: Rocket = new Rocket(new Booster())
rocket.launch();

// Will represent the correct distance travelled
rocket.distanceTravelled
