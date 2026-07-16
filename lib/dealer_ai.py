def make_decision(bullets_list):
    """
    Analiza la lista de balas restantes en la escopeta y decide la acción del Dealer.
    Retorna: "SHOOT_PLAYER" o "SHOOT_DEALER"
    por ahora solo hace esto no esta conectado a nada.. en el proto.1.4 en el siguiente proto se añadira los items
    """
    if not bullets_list:
        return "SHOOT_DEALER" # Respaldo de seguridad en caso de escopeta vacía
        
    lives = bullets_list.count("live")
    blanks = bullets_list.count("blank")
    total = len(bullets_list)
    
    # Calcular probabilidad matemática de bala real
    prob_live = lives / total
    
    # Si hay más probabilidad de bala real, dispara al jugador.
    # Si hay igual o mayor probabilidad de bala falsa, se dispara a sí mismo.
    if prob_live > 0.5:
        return "SHOOT_PLAYER"
    else:
        return "SHOOT_DEALER"