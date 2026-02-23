from cards.infrastructure.flows import match_card

FLOWS = {
    match_card.FLOW_NAME: match_card.match_card_flow,
}
