sealed trait UnitsModule {
  type Kilometres
  type Miles

  val ZeroKm: Kilometres
  val ZeroMi: Miles

  def kilometres(value: Double): Option[Kilometres]
  def miles(value: Double): Option[Miles]

  def add(km1: Kilometres, km2: Kilometres): Kilometres
  def toKm(miles: Miles): Kilometres
}

val Units: UnitsModule = new UnitsModule {
  type Kilometres = Double
  type Miles = Double

  val ZeroKm: Kilometres = 0
  val ZeroMi: Miles = 0

  def kilometres(value: Double): Option[Kilometres] = if (value < 0) None else Some(value)
  def miles(value: Double): Option[Miles] = if (value < 0) None else Some(value)

  def add(km1: Kilometres, km2: Kilometres): Kilometres = km1 + km2
  def toKm(miles: Miles): Kilometres = miles * 1.6
}

import Units._

class Booster() {
  def provideLaunchBoost(): Miles = miles(100).getOrElse(ZeroMi)
}

class Rocket(booster: Booster) {
  private var distance: Kilometres = ZeroKm

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
