"""
Reusable animation helpers for Imajin Image Processor

This module provides common animation functions using PyQt6's QPropertyAnimation
to create smooth, consistent transitions throughout the application.
"""

from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QSequentialAnimationGroup, QParallelAnimationGroup, Qt
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from .theme import Theme


def fade_in(widget, duration=None, callback=None):
    """
    Fade widget from 0 to 1 opacity

    Args:
        widget: QWidget to animate
        duration: Animation duration in ms (defaults to Theme.ANIMATION_NORMAL)
        callback: Optional function to call when animation finishes

    Returns:
        QPropertyAnimation instance
    """
    if duration is None:
        duration = Theme.ANIMATION_NORMAL

    # Create opacity effect
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)

    # Create animation
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(duration)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    if callback:
        animation.finished.connect(callback)

    animation.start()
    return animation


def fade_out(widget, duration=None, callback=None):
    """
    Fade widget from 1 to 0 opacity

    Args:
        widget: QWidget to animate
        duration: Animation duration in ms (defaults to Theme.ANIMATION_NORMAL)
        callback: Optional function to call when animation finishes

    Returns:
        QPropertyAnimation instance
    """
    if duration is None:
        duration = Theme.ANIMATION_NORMAL

    # Get or create opacity effect
    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsOpacityEffect):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)

    # Create animation
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(duration)
    animation.setStartValue(1.0)
    animation.setEndValue(0.0)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    if callback:
        animation.finished.connect(callback)

    animation.start()
    return animation


def slide_in(widget, direction='down', duration=None, callback=None):
    """
    Slide widget in from edge

    Args:
        widget: QWidget to animate
        direction: Direction to slide from ('down', 'up', 'left', 'right')
        duration: Animation duration in ms (defaults to Theme.ANIMATION_NORMAL)
        callback: Optional function to call when animation finishes

    Returns:
        QPropertyAnimation instance
    """
    if duration is None:
        duration = Theme.ANIMATION_NORMAL

    # Store original position
    start_pos = widget.pos()

    # Calculate offset based on direction
    offsets = {
        'down': QPoint(0, -widget.height()),
        'up': QPoint(0, widget.height()),
        'left': QPoint(widget.width(), 0),
        'right': QPoint(-widget.width(), 0)
    }

    offset = offsets.get(direction, QPoint(0, -widget.height()))

    # Move widget to offset position
    widget.move(start_pos + offset)
    widget.show()

    # Create animation
    animation = QPropertyAnimation(widget, b"pos")
    animation.setDuration(duration)
    animation.setStartValue(start_pos + offset)
    animation.setEndValue(start_pos)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    if callback:
        animation.finished.connect(callback)

    animation.start()
    return animation


def slide_out(widget, direction='down', duration=None, callback=None):
    """
    Slide widget out to edge

    Args:
        widget: QWidget to animate
        direction: Direction to slide to ('down', 'up', 'left', 'right')
        duration: Animation duration in ms (defaults to Theme.ANIMATION_NORMAL)
        callback: Optional function to call when animation finishes

    Returns:
        QPropertyAnimation instance
    """
    if duration is None:
        duration = Theme.ANIMATION_NORMAL

    # Store original position
    start_pos = widget.pos()

    # Calculate offset based on direction
    offsets = {
        'down': QPoint(0, widget.height()),
        'up': QPoint(0, -widget.height()),
        'left': QPoint(-widget.width(), 0),
        'right': QPoint(widget.width(), 0)
    }

    offset = offsets.get(direction, QPoint(0, widget.height()))

    # Create animation
    animation = QPropertyAnimation(widget, b"pos")
    animation.setDuration(duration)
    animation.setStartValue(start_pos)
    animation.setEndValue(start_pos + offset)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    if callback:
        animation.finished.connect(callback)

    animation.start()
    return animation


def scale_bounce(widget, scale=1.1, duration=None, callback=None):
    """
    Quick scale up and bounce back animation

    Args:
        widget: QWidget to animate
        scale: Scale factor (e.g., 1.1 for 10% larger)
        duration: Total animation duration in ms (defaults to Theme.ANIMATION_FAST)
        callback: Optional function to call when animation finishes

    Returns:
        QSequentialAnimationGroup instance
    """
    if duration is None:
        duration = Theme.ANIMATION_FAST

    # Get original geometry
    original_geo = widget.geometry()

    # Calculate scaled geometry (centered)
    scaled_width = int(original_geo.width() * scale)
    scaled_height = int(original_geo.height() * scale)
    scaled_x = original_geo.x() - (scaled_width - original_geo.width()) // 2
    scaled_y = original_geo.y() - (scaled_height - original_geo.height()) // 2

    scaled_geo = widget.geometry()
    scaled_geo.setRect(scaled_x, scaled_y, scaled_width, scaled_height)

    # Create sequential animation group
    group = QSequentialAnimationGroup()

    # Scale up animation
    scale_up = QPropertyAnimation(widget, b"geometry")
    scale_up.setDuration(duration // 2)
    scale_up.setStartValue(original_geo)
    scale_up.setEndValue(scaled_geo)
    scale_up.setEasingCurve(QEasingCurve.Type.OutCubic)

    # Scale down animation
    scale_down = QPropertyAnimation(widget, b"geometry")
    scale_down.setDuration(duration // 2)
    scale_down.setStartValue(scaled_geo)
    scale_down.setEndValue(original_geo)
    scale_down.setEasingCurve(QEasingCurve.Type.OutCubic)

    group.addAnimation(scale_up)
    group.addAnimation(scale_down)

    if callback:
        group.finished.connect(callback)

    group.start()
    return group


def pulse(widget, property_name=b"windowOpacity", min_value=0.7, max_value=1.0, duration=None):
    """
    Create infinite pulsing animation

    Args:
        widget: QWidget to animate
        property_name: Property to animate (default: windowOpacity)
        min_value: Minimum property value
        max_value: Maximum property value
        duration: Duration of one pulse cycle in ms (defaults to Theme.ANIMATION_SLOW)

    Returns:
        QPropertyAnimation instance
    """
    if duration is None:
        duration = Theme.ANIMATION_SLOW

    animation = QPropertyAnimation(widget, property_name)
    animation.setDuration(duration)
    animation.setStartValue(min_value)
    animation.setEndValue(max_value)
    animation.setLoopCount(-1)  # Infinite loop
    animation.setEasingCurve(QEasingCurve.Type.InOutSine)

    # Make it alternate direction
    animation.setDirection(QPropertyAnimation.Direction.Forward)

    animation.start()
    return animation


def smooth_height_change(widget, target_height, duration=None, callback=None):
    """
    Smoothly animate widget height change

    Args:
        widget: QWidget to animate
        target_height: Target height in pixels
        duration: Animation duration in ms (defaults to Theme.ANIMATION_NORMAL)
        callback: Optional function to call when animation finishes

    Returns:
        QPropertyAnimation instance
    """
    if duration is None:
        duration = Theme.ANIMATION_NORMAL

    animation = QPropertyAnimation(widget, b"maximumHeight")
    animation.setDuration(duration)
    animation.setStartValue(widget.height())
    animation.setEndValue(target_height)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    if callback:
        animation.finished.connect(callback)

    animation.start()
    return animation


def smooth_scroll_to_bottom(scroll_area, duration=None):
    """
    Smoothly scroll a QScrollArea to the bottom

    Args:
        scroll_area: QScrollArea or QAbstractScrollArea to animate
        duration: Animation duration in ms (defaults to Theme.ANIMATION_FAST)

    Returns:
        QPropertyAnimation instance
    """
    if duration is None:
        duration = Theme.ANIMATION_FAST

    scrollbar = scroll_area.verticalScrollBar()

    animation = QPropertyAnimation(scrollbar, b"value")
    animation.setDuration(duration)
    animation.setStartValue(scrollbar.value())
    animation.setEndValue(scrollbar.maximum())
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    animation.start()
    return animation


def rotate_icon(widget, property_name=b"rotation", duration=None):
    """
    Create infinite rotation animation (for loading spinners)

    Args:
        widget: QWidget to animate
        property_name: Property to animate
        duration: Duration of one full rotation in ms (defaults to Theme.ANIMATION_SLOW)

    Returns:
        QPropertyAnimation instance
    """
    if duration is None:
        duration = Theme.ANIMATION_SLOW

    animation = QPropertyAnimation(widget, property_name)
    animation.setDuration(duration)
    animation.setStartValue(0)
    animation.setEndValue(360)
    animation.setLoopCount(-1)  # Infinite loop
    animation.setEasingCurve(QEasingCurve.Type.Linear)

    animation.start()
    return animation


def color_transition(widget, stylesheet_property, from_color, to_color, duration=None, callback=None):
    """
    Smoothly transition color by updating stylesheet

    Note: This is a simplified version. For complex color transitions,
    consider using QGraphicsColorizeEffect or custom painting.

    Args:
        widget: QWidget to animate
        stylesheet_property: CSS property to update (e.g., 'background-color')
        from_color: Starting color (hex string)
        to_color: Ending color (hex string)
        duration: Animation duration in ms (defaults to Theme.ANIMATION_NORMAL)
        callback: Optional function to call when animation finishes

    Returns:
        None (updates stylesheet directly)
    """
    if duration is None:
        duration = Theme.ANIMATION_NORMAL

    # Parse colors
    from_r = int(from_color[1:3], 16)
    from_g = int(from_color[3:5], 16)
    from_b = int(from_color[5:7], 16)

    to_r = int(to_color[1:3], 16)
    to_g = int(to_color[3:5], 16)
    to_b = int(to_color[5:7], 16)

    # Create animation timer
    from PyQt6.QtCore import QTimer, QPropertyAnimation
    steps = duration // 16  # ~60 FPS
    current_step = [0]  # Use list to allow modification in closure

    def update_color():
        current_step[0] += 1
        progress = current_step[0] / steps

        # Interpolate RGB values
        r = int(from_r + (to_r - from_r) * progress)
        g = int(from_g + (to_g - from_g) * progress)
        b = int(from_b + (to_b - from_b) * progress)

        color_hex = f"#{r:02x}{g:02x}{b:02x}"

        # Update stylesheet
        widget.setStyleSheet(f"{stylesheet_property}: {color_hex};")

        if current_step[0] >= steps:
            timer.stop()
            if callback:
                callback()

    timer = QTimer()
    timer.timeout.connect(update_color)
    timer.start(16)  # ~60 FPS

    return timer
