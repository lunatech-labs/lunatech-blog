sealed trait UnitsModule {
  type Kilometers
  type Miles

  val ZeroKm: Kilometers
  val ZeroMi: Miles

  def kilometres(value: Double): Option[Kilometers]
  def miles(value: Double): Option[Miles]

  def add(km1: Kilometers, km2: Kilometers): Kilometers
  def toKilometers(miles: Miles): Kilometers
}

val Units = new UnitsModule {
  type Kilometers = Double
  type Miles = Double

  val ZeroKm: Kilometers = 0
  val ZeroMi: Miles = 0

  def kilometres(value: Double): Option[Kilometers] = if (value < 0) None else Some(value)
  def miles(value: Double): Option[Miles] = if (value < 0) None else Some(value)

  def add(km1: Kilometers, km2: Kilometers): Kilometers = km1 + km2
  def toKilometers(miles: Miles): Kilometers = miles * 1.6
}

import Units._


class Booster() {
  def provideLaunchBoost(): Miles = miles(100).getOrElse(ZeroMi)
}

class Rocket(booster: Booster) {
  private var distance: Kilometers = ZeroKm

  def launch(): Unit = {
    // Kilometers and Miles are once again transparent so back to initial bug
    distance += booster.provideLaunchBoost()
  }

  def distanceTravelled: Kilometers = distance
}

val rocket: Rocket = new Rocket(new Booster())
rocket.launch();

// Will think it has travelled 100km rather than 160km
rocket.distanceTravelled